

# LOG

*update  2017 - 3 -16*

**微信登陆页面**
https://open.weixin.qq.com/connect/oauth2/authorize?appid=wx85625e403869c2e1&redirect_uri=http%3a%2f%2fwww.zvoter.com%2fweixin_auth&response_type=code&scope=snsapi_userinfo&state=123#wechat_redirect

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



-----





*update: 2017-03-06*

以下是以 https://github.com/justonlyyo/zvoter 中的 zvoter_mon 分支为基准的变更记录：

**对于投票页面进行了小的修改。**

1. 添加 user_center_voter.js
2. 修改 user_center_voter.html 的左侧信息部分，删除“我收藏的投票”, 在我发布的投票和我参加的投票右侧添加计数
3. 修改 flask_server 中 user_center_voter 函数
4. 修改 topic.py 中的 fetch_joined_topics 函数，并删除了 fetch_starred_topics 函数

**添加通知中心的页面**

5. 添加 user_center_notification 的 .html 和 .js 文件
6. 在 user_center_info.css 中添加 user_center_notification 部分（见代码最后）
7. 添加 notification.py 文件，用于消息的推送相关函数
8. 在 flask_server.py 中添加 user_center_notification 函数处理页面，并添加 mark_notification 函数设置消息的已读
9. 数据库中添加新的 notification 表，结构如下：

<table>
<tr><td>user_id</td><td>用户id</td></tr>
<tr><td>topic_id</td><td>话题id</td></tr>
<tr><td>detail</td><td>通知细节</td></tr>
<tr><td>read</td><td>已读（0为未读，1为已读）</td></tr>
<tr><td>date</td><td>通知第一次创建的时间</td></tr>
</table>
