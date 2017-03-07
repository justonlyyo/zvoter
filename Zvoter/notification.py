# -*- coding:utf8 -*-
import my_db
import sqlalchemy.exc
import datetime
import re
import json


def get_columns(first=False):
    """获取所有的user_info表的列名，只在启动程序时运行一次,参数
    first是代表是否第一次启动，如果第一次启动要强制重新加载列名"""
    redis_client = my_db.MyRedis.redis_client()
    value = redis_client.get("notification_columns")
    if value is None or first:
        sql = "SHOW columns FROM notification"
        session = my_db.sql_session()
        proxy_result = session.execute(sql)
        session.close()
        result = proxy_result.fetchall()
        value = json.dumps([x[0] for x in result]).encode()
        redis_client.set('notification', value)
    return json.loads(value.decode())


get_columns(True)  # 第一次启动时加载


def add(user_id, detail):
    """对某个用户添加一个新的消息通知。
    当遇到评论过千、审核通过时，调用此方法将消息写入数据库。
    detail为通知的详细内容。"""
    session = my_db.sql_session()
    sql = "insert into zvoter.notification (`user_id`, `detail`, `read`, `date`) values ('{}', '{}', {}, '{}')".\
        format(user_id, detail, 0, my_db.current_datetime())
    session.execute(sql)
    session.commit()


def fetch_by_user_id(user_id):
    """根据用户id获取其通知信息"""
    session = my_db.sql_session()
    columns = get_columns()
    sql = "select * from notification where user_id = {} order by date desc".format(user_id)
    data = []
    try:
        proxy_result = session.execute(sql)
        result = proxy_result.fetchall()
        if len(result) != 0:
            result = [my_db.str_format(x) for x in result]
            data = [dict(zip(columns, x)) for x in result]
        else:
            data = []
    except Exception as e:
        print(e)
    finally:
        session.close()
    return data


def mark_as_read(notification_id):
    """根据用户id标记消息为已读"""
    session = my_db.sql_session()
    sql = "update notification set `read` = 1 where notification_id = {}".format(notification_id)
    session.execute(sql)
    session.commit()


# add(17022016502781053829, "您的xxxxxxxx话题审核通过")
# add(17022016502781053829, "您的yyyyyyyyy话题评论过千")
# mark_as_read(5)
# print(fetch_by_user_id(17022016502781053829))

