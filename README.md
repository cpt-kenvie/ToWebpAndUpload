## 缘由

兰空图床本身并未提供压缩上传功能，而我又期望能实现极致的加载速度，于是便自行利用兰空图床 API 编写了一个 Python 脚本来达成此目的。

## 介绍

使用 Python Flask 框架编写一个页面，在该页面中能够将图片压缩为 webp 格式，然后上传至兰空图床。

此项目运用 Python Flask 框架构建了一个页面，在该页面中，能够把图片压缩成 webp 格式，随后上传至兰空图床。目前仅实现了游客上传功能（我在测试过程中遇到了些问题，我作为一名小白，带着 Authorization 进行验证时一直失败。我再看看，或者有大牛帮我写，嘻嘻）。

## 准备

在成功搭建[兰空图床](https://github.com/lsky-org/lsky-pro)后，需在 app.py 中找到以下这行代码，并将其修改为您所搭建兰空图床的实际地址：

```python
def upload_to_api(file_path, file_name):
    conn = http.client.HTTPSConnection("img.kenvie.com")
```

## 启动

安装所需依赖：

```shell
pip install flask pillow
```

启动程序：

```shell
python app.py
```

