from flask import Flask, render_template, request, send_from_directory, redirect, url_for, jsonify
import os
from PIL import Image
from werkzeug.utils import secure_filename
import uuid
import http.client
import mimetypes
from codecs import encode
import json

app = Flask(__name__)

# 设置允许上传的文件类型和上传文件夹
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

# 创建目录（如果不存在）
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# 判断文件是否为允许上传的类型
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 图片压缩并转换为 WebP 格式
def compress_and_convert_to_webp(input_path, output_path, quality=85):
    try:
        img = Image.open(input_path)
        img.save(output_path, 'WebP', quality=quality, method=6)  # 高压缩级别
        print(f"压缩并转换完成：{input_path} -> {output_path}")
    except Exception as e:
        print(f"转换过程中出错: {e}")

# 上传文件到 API
def upload_to_api(file_path, file_name):
    conn = http.client.HTTPSConnection("img.kenvie.com")
    boundary = 'wL36Yn8afVp8Ag7AmP8qZ0SA4n1v9T'
    dataList = []
    dataList.append(encode('--' + boundary))
    file_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
    dataList.append(encode(f'Content-Disposition: form-data; name=file; filename={file_name}'))
    dataList.append(encode(f'Content-Type: {file_type}'))
    dataList.append(encode(''))
    
    with open(file_path, 'rb') as f:
        file_data = f.read()
    dataList.append(file_data)
    dataList.append(encode('--' + boundary))

    # 添加其他字段（例如strategy_id）
    dataList.append(encode('Content-Disposition: form-data; name=strategy_id;'))
    dataList.append(encode('Content-Type: text/plain'))
    dataList.append(encode(''))
    dataList.append(encode("2"))
    dataList.append(encode('--' + boundary + '--'))
    dataList.append(encode(''))

    body = b'\r\n'.join(dataList)
    headers = {
        'Content-Type': f'multipart/form-data; boundary={boundary}',
        'Accept': 'application/json'
    }

    conn.request("POST", "/api/v1/upload", body, headers)
    res = conn.getresponse()
    return res.read().decode("utf-8")

# 主页，显示上传表单
@app.route('/')
def index():
    return render_template('index.html')

# 处理文件上传并转换
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}.webp"
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        output_path = os.path.join(app.config['PROCESSED_FOLDER'], unique_filename)
        
        # 保存上传的文件
        file.save(input_path)
        
        # 压缩并转换图片
        compress_and_convert_to_webp(input_path, output_path)
        
        # 删除原始文件（可选）
        os.remove(input_path)

        # 上传到 API
        response_data = upload_to_api(output_path, unique_filename)

        # 将字符串转换为 JSON 对象
        response_json = json.loads(response_data)

        # 检查 API 返回的状态
        if not response_json.get("status"):
            return jsonify({'error': response_json.get("message")})

        # 提供下载链接
        return jsonify({'message': response_json})

    return jsonify({'error': '文件上传失败，请重试。'})

# 提供下载链接
@app.route('/uploads/<filename>')
def download_file(filename):
    return send_from_directory(app.config['PROCESSED_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
