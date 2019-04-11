from qiniu import Auth, put_file, etag,put_data
import qiniu.config


# 需要填写你的 Access Key 和 Secret Key
access_key = 'v3n5FPnRvLujRroKe3X9FxjMSgtWCmMWBeharusu'
secret_key = 'd3uJUlaQ9iKh0b5XkhU-Tlx5hjrDiWDDeHA4xotw'
#要上传的空间
bucket_name = 'info8'
#构建鉴权对象
q = Auth(access_key, secret_key)

def storge(data):
    try:
        # 生成上传 Token，可以指定过期时间等
        token = q.upload_token(bucket_name, None, 3600)
        # print(token)
        # 要上传文件的本地路径
        # localfile = './11.jpg'
        # ret, info = put_file(token, None, localfile)
        ret, info = put_data(token, None, data)


        # if info.status_code == 200:
        #     return ret.get("key")
        # else:
        #     return "aa"
        # 上传成功,返回图片名称,失败返回空
        return ret.get("key")
    except Exception as e:
        raise Exception("上传头像错误")


if __name__ == '__main__':
    file = open(r'G:\python\my_object\see_new\info\static\news\images\bg01.jpg', 'rb')
    print(storge(file.read()))
    file.close()