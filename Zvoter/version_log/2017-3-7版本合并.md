Log
===

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
