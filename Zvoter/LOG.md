

# LOG

UPDATE  2017 - 3 -16



**数据库基础改动**

1. 用户头像 user_img_url 从 100 位改为 200 位，这是微信服务器头像长度导致的。
2. user_phone 的 UNIQUE 属性删除，因为微信登陆不一定要电话号码。



**微信服务器认证相关**

1. 在 static 目录下添加 MP_verify_RZO0Fo2eVSv0Gt29.txt 文件，用于微信服务器检测。
2. 在 flask-server 中添加 weixin_verification 函数，返回 MP_verify_RZO0Fo2eVSv0Gt29.txt 文件。



**微信登陆相关代码**

1. 在 flask-server 中添加 weixin_auth 函数，作为微信登陆的入口
2. 在 flask-server 中添加 weixin_new_user 函数，作为微信注册为新用户的入口
3. 在 flask-server 中修改 my_login 函数，在里面加入绑定微信的代码



**用于支持微信登陆，修改用户工具类的相关代码**

1. 在 user.py 中添加 check_wx 用于检测用户微信是否已经注册过
2. 在 user.py 中添加 check_phone_registered 用于检测是否手机是否注册过
3. 修改 user.py 中的 add_user，对于微信登录，允许手机号不存在
4. 修改 user.py 中的 check_user_args，主要是 openid 和 img_url 中包含特殊字符会被这个函数过滤掉
5. 修改 user.py 中的 edit_user， 微小的改动



**微信登陆页面**

1. 添加了 user_weixin_binding.html / js / css 三个对应的文件



**潜在的 BUG**

1. 微信提供的地点可能不含省市，与数据库不一致，例如微信提供“上海”，但是个人中心的地点是“上海市”，会出现报错。因为一个地理位置的字典里，有“上海市”这个键，没有“上海”。因此微信的地理位置暂时并没有整合进去。