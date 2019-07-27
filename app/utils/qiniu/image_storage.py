from qiniu import Auth, put_data

access_key = "r0qQvspGzBJQT2Q6SbmovV7cWqIUy9JEb9CNDt_Q"
secret_key = "GY9TtpHqY6lJSamBFw0k7gCAGPMdlKFJKgYAOqf9"
bucket_name = "storage"


def storage(data):
    try:
        q = Auth(access_key, secret_key)
        token = q.upload_token(bucket_name)
        ret, info = put_data(token, None, data)
        print(ret, info)
    except Exception as e:
        raise e;

    if info.status_code != 200:
        raise Exception("上传图片失败")
    return ret["key"]#具体地址


if __name__ == '__main__':
    file = input('请输入文件路径')
    with open(file, 'rb') as f:#读文件的基础操作 ，rb二进制形式读取
        storage(f.read())