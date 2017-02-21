# -*- coding:utf8 -*-
import my_db
import json

"""话题的操作"""


def get_columns(first=False):
    """获取所有的topic_info表的列名，只在启动程序时运行一次,参数
    first是代表是否第一次启动，如果第一次启动要强制重新加载列名"""
    redis_client = my_db.MyRedis.redis_client()
    value = redis_client.get("topic_info_columns")
    if value is None or first:
        sql = "SHOW columns FROM topic_info"
        session = my_db.sql_session()
        proxy_result = session.execute(sql)
        session.close()
        result = proxy_result.fetchall()
        value = json.dumps([x[0] for x in result]).encode()
        redis_client.set('topic_info_columns', value)
    return json.loads(value.decode())


get_columns(True)  # 第一次启动时加载


def manage_topic(**kwargs):
    """用户对话题的管理"""
    message = {"message": "success"}
    try:
        the_type = kwargs.pop("the_type")
        if the_type == "add":
            """添加"""
            if kwargs['begin_date'] == "":
                kwargs['begin_date'] = my_db.current_datetime()
            if kwargs['end_date'] == "":
                kwargs['end_date'] = my_db.current_datetime(365)
            kwargs['can_show'] = 0
            sql = my_db.structure_sql("add", "topic_info", **kwargs)
            sql_session = my_db.sql_session()
            print(sql)
            sql_session.execute(sql)
            sql_session.commit()
            sql_session.close()

        elif the_type == "edit":
            pass
    except KeyError:
        message['message'] = "不理解的操作"
    except Exception as e:
        message['message'] = "数据库执行错误"
        print(e)
    finally:
        return message


def topic_count():
    """统计所有话题的数量"""
    sql_session = my_db.sql_session()
    sql = "select count(1) from topic_info"
    proxy = sql_session.execute(sql)
    result = proxy.fetchone()[0]
    sql_session.close()
    return result


def manage_topic_admin(**kwargs):
    """后台对话题的管理"""
    message = {"message": "success"}
    sql_session = my_db.sql_session()
    try:
        the_type = kwargs.pop("the_type")
        if the_type == "add":
            """添加"""
            if kwargs['begin_date'] == "":
                kwargs['begin_date'] = my_db.current_datetime()
            if kwargs['end_date'] == "":
                kwargs.pop('end_date')
            kwargs['can_show'] = 0
            sql = my_db.structure_sql("add", "topic_info", **kwargs)
            print(sql)
            sql_session.execute(sql)
            sql_session.commit()

        elif the_type == "edit":
            """编辑"""
            try:
                top_id = kwargs.pop("top_id")
                if kwargs['begin_date'] == "":
                    kwargs['begin_date'] = my_db.current_datetime()
                if kwargs['end_date'] == "":
                    kwargs['end_date'] = my_db.current_datetime(365)
                sql = my_db.structure_sql("edit", "topic_info", "where top_id='{}'".format(top_id), **kwargs)
                sql_session.execute(sql)
                sql_session.commit()
            except KeyError:
                message['message'] == '错误的话题id'
            except Exception as e:
                message['message'] = "数据库执行错误"
                print(e)

        elif the_type == "drop":
            """删除"""
            try:
                top_id = kwargs.pop("top_id")
                sql = "delete from topic_info where top_id={}".format(top_id)
                sql_session.execute(sql)
                sql_session.commit()
            except KeyError:
                message['message'] == '错误的话题id'
            except Exception as e:
                message['message'] = "数据库执行错误"
                print(e)

        elif the_type == "up":
            """话题对用户可见"""
            try:
                top_id = kwargs.pop("top_id")
                sql = "update topic_info set can_show=1 where top_id={}".format(top_id)
                sql_session.execute(sql)
                sql_session.commit()
            except KeyError:
                message['message'] == '错误的话题id'
            except Exception as e:
                message['message'] = "数据库执行错误"
                print(e)

        elif the_type == "down":
            """话题对用户不可见"""
            try:
                top_id = kwargs.pop("top_id")
                sql = "update topic_info set can_show=0 where top_id={}".format(top_id)
                sql_session.execute(sql)
                sql_session.commit()
            except KeyError:
                message['message'] == '错误的话题id'
            except Exception as e:
                message['message'] = "数据库执行错误"
                print(e)

        elif the_type == "single":
            """根据id获取单个话题的内容"""
            top_id = kwargs.pop("top_id")
            sql = "SELECT top_id,top_title,top_content,viewpoint_a,viewpoint_b,can_show,img_url_a,img_url_b," \
                  "channel_info.channel_name,class_info.class_name,end_date,begin_date," \
                  "user_info.user_nickname FROM topic_info,channel_info,class_info,user_info "\
                  "WHERE user_info.user_id=topic_info.author " \
                  "AND channel_info.channel_id=topic_info.channel_id and " \
                  "class_info.class_id=topic_info.class_id AND  " \
                  "top_id='{}'".format(top_id)
            columns = ['top_id', 'top_title', 'top_content', 'viewpoint_a', 'viewpoint_b', 'can_show',
                       'img_url_a', 'img_url_b', 'channel_name', 'class_name', 'end_date', 'begin_date', 'author']
            proxy_result = sql_session.execute(sql)
            result = proxy_result.fetchone()
            result = my_db.str_format(result)
            data = dict(zip(columns, result))
            message['data'] = data

        elif the_type == "page":
            """分页查询话题"""
            index = kwargs.get("index")
            length = kwargs.get("page_length")
            try:
                index = int(index)
                length = int(length)
                columns = get_columns()
                sql = "select " + ",".join(columns) + (" from topic_info order by create_date desc "
                                                       "limit {},{}".format((index - 1) * length, length))
                try:
                    proxy_result = sql_session.execute(sql)
                    result = proxy_result.fetchall()
                    if len(result) != 0:
                        result = [my_db.str_format(x) for x in result]
                        data = [dict(zip(columns, x)) for x in result]
                    else:
                        data = []
                    message['data'] = data
                except Exception as e:
                    print(e)
                    message['message'] = "查询错误"
            except ValueError:
                message['message'] = "无效的页码或者步长"

    except KeyError:
        message['message'] = "不理解的操作"
    except Exception as e:
        print(e)
        message['message'] = "数据库执行错误"
    finally:
        sql_session.close()
        return message


def index_list():
    """获取个频道最新的话题列表"""