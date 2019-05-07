from django.conf import settings
from urllib.parse import urlencode,parse_qs
from urllib.request import urlopen
from .exceptions import QQAPIException
import logging,json

logger=logging.getLogger('django')



#用于qq登陆的工具类，提供qq登陆用的方法
class OAuthQQ(object):

    def __init__(self,app_id=None,app_key=None,redirect_url=None,state=None):
        self.app_id=app_id or settings.QQ_APP_ID
        self.app_key=app_key or settings.QQ_APP_KEY
        self.redirect_url=redirect_url or settings.QQ_REDIRECT_URL
        self.state=state or settings.QQ_STATE




    #拼接连接地址
    def generate_qq_login_url(self):
        url='https://graph.qq.com/oauth2.0/authorize?'
        data={
            "response_type":"code",
            "client_id":self.app_id,
            "redirect_uri":self.redirect_url,
            "state":self.state,
            "scope":'get_user_info'
        }
        query_string=urlencode(data)
        url+=query_string

        return url
    #向qq服务器发起请求获取accesstoken
    def get_access_token(self,code):
        #将参数拼接在要请求的qq网址中
        url='https://graph.qq.com/oauth2.0/token?'
        data={
        'grant_type': 'authorization_code',
        'client_id': self.app_id,
        'client_secret': self.app_key,
        'code': code,
        'redirect_uri': self.redirect_url,
}
        url+=urlencode(data)
        try:
            #发送请求,返回如下数据
            # access_token=FE04************************CCE2&expires_in=7776000&refresh_token=88E4************************
            response=urlopen(url)
            #读取数据
            response=response.read().decode()#type:str
            #将以上字符串转换
            response=parse_qs(response)#type:dict
            access_token=response.get('access_token')[0]
        except Exception as e:
            logger.error(e)
            raise QQAPIException('获取access_token异常')
        return  access_token

    # 凭借token向qq服务器发送请求获取openid
    def get_openid(self,token):
        url='https://graph.qq.com/oauth2.0/me?access_token='+token
        try:
            response = urlopen(url)
            # 读取数据
            # callback( {"client_id":"YOUR_APPID","openid":"YOUR_OPENID"} )\n;
            response_data = response.read().decode()
            data=json.loads(response_data[10:-4])
        except Exception:
            data=parse_qs(response_data)
            logger.error('code=%s msg=%s'%(data.get('code'),data.get('msg')))
            raise QQAPIException('获取openid异常')
        openid=data.get('openid',None)
        return openid






