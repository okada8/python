本程序是新闻浏览器程序，所实现功能如下：
1.多账户登录，登录密码输错3次被锁定5分钟，登录状态验证
2.管理员账户有发布新闻，删除新闻，查看日志，锁定账户，解锁账户，查看意见
3.普通用户功能查看新闻，加入收藏，查看收藏，删除指定收藏，反馈意见，指定内容搜索新闻,浏览次数查看，根据浏览次数排序
4.管理员日志和普通用户日志分开
5.当输入用户不存在会进行注册
6.注册用到MD5验证，邮箱验证，四位随机验证码
7.可以被放在任何目录下，直接用py.exe来运行
8.用到configparser，json，re，logging，time，os，sys，random，hashlib模块


