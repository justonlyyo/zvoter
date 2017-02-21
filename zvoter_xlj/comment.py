# -*- coding:utf8 -*-
import my_db
import json

"""留言管理模块"""


def get_columns(first=False):
    """获取所有的topic_info表的列名，只在启动程序时运行一次,参数
    first是代表是否第一次启动，如果第一次启动要强制重新加载列名"""
    redis_client = my_db.MyRedis.redis_client()
    value = redis_client.get("comment_info_columns")
    if value is None or first:
        sql = "SHOW columns FROM comment_info"
        session = my_db.sql_session()
        proxy_result = session.execute(sql)
        session.close()
        result = proxy_result.fetchall()
        value = json.dumps([x[0] for x in result]).encode()
        redis_client.set('comment_info_columns', value)
    return json.loads(value.decode())


def manage_comment(**kwargs):
    """管理用户留言"""
    message = {"message": "success"}
    sql_session = my_db.sql_session()
    try:
        the_type = kwargs.pop("the_type")
        if the_type == "add":
            """添加留言"""
            pass
    except KeyError:
        message['message'] = "不理解的操作"
    except Exception as e:
        print(e)
        message['message'] = "数据库执行错误"
    finally:
        sql_session.close()
        return message
