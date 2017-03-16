# -*- coding:utf8 -*-
import my_db
import json
from channel import channel_list
from channel import get_class_list
from vote_tools import get_view_count
from vote_tools import sum_vote_count

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

            child_sql = "(SELECT CONCAT_WS(' vs ',SUM(support_a),SUM(support_b))  " \
                        "FROM vote_count WHERE vote_count.topic_id=topic_info.top_id)"  # 查询ab支持度的子查询
            sql = "SELECT top_id,top_title,top_content,viewpoint_a,viewpoint_b,can_show,img_url_a,img_url_b," \
                  "topic_info.channel_id,channel_info.channel_name,topic_info.class_id," \
                  "class_info.class_name,end_date,begin_date," \
                  "user_info.user_nickname,{} FROM topic_info,channel_info,class_info,user_info " \
                  "WHERE user_info.user_id=topic_info.author " \
                  "AND channel_info.channel_id=topic_info.channel_id and " \
                  "class_info.class_id=topic_info.class_id AND  " \
                  "top_id='{}'".format(child_sql, top_id)
            columns = ['top_id', 'top_title', 'top_content', 'viewpoint_a', 'viewpoint_b', 'can_show',
                       'img_url_a', 'img_url_b', 'channel_id', 'channel_name', 'class_id', 'class_name', 'end_date',
                       'begin_date', 'author', "a_vs_b"]
            proxy_result = sql_session.execute(sql)
            result = proxy_result.fetchone()
            result = my_db.str_format(result)
            sql_session.close()
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


"""分支版本追加的函数，个人中心用，代码区段开始"""


def fetch_topics_by_id_list(ids):
    """根据话题id列表获取话题内容"""
    session = my_db.sql_session()
    columns = get_columns()
    id_lists = ",".join(map(lambda x: str(x), ids))
    sql = "select * from topic_info where top_id in ({})".format(id_lists)
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


def fetch_created_topics(user_id):
    """根据用户id获取创建过的话题"""
    session = my_db.sql_session()
    columns = get_columns()
    sql = "select * from topic_info where author = {}".format(user_id)
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


def fetch_joined_topics(user_id):
    """根据用户id获取参加过的话题"""
    session = my_db.sql_session()
    columns = get_columns()
    sql = "select * from topic_info where top_id in " \
          "(select topic_id from vote_count where user_id = {})" \
        .format(user_id)
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


"""分支版本追加的函数，个人中心用，代码区段结束"""


def topic_detail_user(top_id):
    """用户根据id获取单个话题的详细内容,参数中必须要有一个top_id"""
    ses = my_db.sql_session()
    message = {'message': "success"}
    child_sql = "(SELECT CONCAT_WS(' vs ',SUM(support_a),SUM(support_b))  " \
                "FROM vote_count WHERE vote_count.topic_id=topic_info.top_id)"  # 查询ab支持度的子查询
    sql = "SELECT top_id,top_title,top_content,viewpoint_a,viewpoint_b,can_show,img_url_a,img_url_b," \
          "topic_info.channel_id,channel_info.channel_name,topic_info.class_id," \
          "class_info.class_name,end_date,begin_date," \
          "user_info.user_nickname,{} FROM topic_info,channel_info,class_info,user_info " \
          "WHERE user_info.user_id=topic_info.author " \
          "AND channel_info.channel_id=topic_info.channel_id and can_show=1 and " \
          "class_info.class_id=topic_info.class_id AND  " \
          "top_id='{}'".format(child_sql, top_id)
    columns = ['top_id', 'top_title', 'top_content', 'viewpoint_a', 'viewpoint_b', 'can_show',
               'img_url_a', 'img_url_b', 'channel_id', 'channel_name', 'class_id', 'class_name', 'end_date',
               'begin_date', 'author', "a_vs_b"]
    proxy_result = ses.execute(sql)
    result = proxy_result.fetchone()
    result = my_db.str_format(result)
    ses.close()
    data = dict(zip(columns, result))
    message['data'] = data
    return message


def __channel_topic_list(order_by='hot', class_id=0, channel_id=0, page_index=1):
    """获取个频道最新的话题列表.order_by代表排序方式,hot,以热度，argue　争议性，
    page_index 代表第几页，一页１２条消息，默认是第一页
    create_date 发布时间，三种排序方式，目前仅可以实现发布时间倒叙排列
    ｃｈａｎｎｅｌ——ｉｄ　是频道信号。
    ｃｌａｓｓ——ｉｄ　是类别信号，
    如果class_id＝０表示是频道页获取信息，反之，则是点击了频道页下面的类别信息的情况。
    查询结果不排除过期的话题。
    """
    every_page = 12  # 每页１２条记录
    ses = my_db.sql_session()
    key_str = "top_id,top_title,viewpoint_a,viewpoint_b,img_url_a,img_url_b"
    """生成ｓｑｌ语句"""
    child_sql = "(SELECT CONCAT_WS(' vs ',SUM(support_a),SUM(support_b))  " \
                "FROM vote_count WHERE vote_count.topic_id=topic_info.top_id)"  # 查询ab支持度的子查询
    if channel_id == 0 and class_id == 0:
        raise ValueError("频道ｉｄ和列别ｉｄ不能为空")
    elif channel_id != 0 and class_id == 0:
        """ｃｌａｓｓ—id为０表示是频道页查询,返回此频道下最新的话题"""
        sql = "select {},{} from topic_info where can_show=1 and channel_id={} order by create_date desc limit {},{}". \
            format(key_str, child_sql, channel_id, (page_index - 1) * every_page, every_page)
    elif class_id != 0:
        """ｃｌａｓｓ—id和channel_id都不为零表示是频道页点击类别的链接时查询"""
        sql = "select {},{} from topic_info where can_show=1 and class_id={} order by " \
              "create_date desc limit {},{}".format(key_str, child_sql, class_id, (page_index - 1) * every_page,
                                                    every_page)

    proxy = ses.execute(sql)
    result = proxy.fetchall()
    ses.close()
    columns = key_str.split(",")
    columns.append("a_vs_b")
    result = [dict(zip(columns, x)) for x in result]
    for x in result:
        x.update({"view_count": get_view_count(x['top_id']), "vote_count": sum_vote_count(x['top_id'])})
    return result


def channel_topic_list(order_by='hot', channel_id=0, class_id=0, page_index=1):
    """高级方法，获取频道正文的话题列表，返回字典的数组"""
    cache = my_db.cache
    class_id_list = [x['class_id'] for x in get_class_list()]
    channel_id_list = [x['channel_id'] for x in channel_list()]
    key = None

    if not isinstance(page_index, int):
        raise ValueError("page_index is not a int type")
    elif isinstance(class_id, int) and class_id in class_id_list:
        """查询类别"""
        key = "topic_list_class_{}_order_by_{}".format(class_id, order_by)
    elif isinstance(channel_id, int) and channel_id in channel_id_list:
        """查询频道"""
        key = "topic_list_channel_{}_order_by_{}".format(channel_id, order_by)
    else:
        pass

    if key is None:
        raise ValueError("channel_id , class_is error")
    else:
        result = cache.get(key)
        if result is None:
            result = __channel_topic_list(order_by=order_by, channel_id=channel_id, class_id=class_id,
                                          page_index=page_index)
            cache.set(key, result, timeout=60)

        return result


def side_bar_topic_list():
    """高级方法，获取侧边栏话题列表,返回ｌｉｓｔ对象"""
    cache = my_db.cache
    key = "side_bar_topic_list"
    result = cache.get(key)
    if result is None:
        key_str = "top_id,top_title"
        columns = key_str.split(",")
        sql = "select {} from topic_info where can_show=1 order by create_date desc limit 0,11".format(key_str)
        ses = my_db.sql_session()
        proxy = ses.execute(sql)
        result = proxy.fetchall()
        ses.close()
        result = [dict(zip(columns, x)) for x in result]
        cache.set(key, result, timeout=60)

    return result


def update_dict(dict_1, dict_2):
    """合并两个字典，并返回第一个"""
    dict_1.update(dict_2)
    return dict_1


def index_topic_list():
    """获取首页的各频道的话题列表，返回的是是字典
    字典以channel_id为ｋｅｙ，值是话题字典的数组，排序以优先级＋发布时间来排序
    这里不包含置顶帖子，置顶帖子会在视图函数中与此结果重新组合。
    """
    cache = my_db.cache
    key = "index_topic_dict"
    index_topic_dict = cache.get(key)
    if index_topic_dict is None:
        """从数据库查询"""
        channel_id_list = [x['channel_id'] for x in channel_list()]
        current_date = my_db.current_datetime()
        index_topic_dict = dict()  # 结果集容器
        columns_str = "channel_id,class_id,top_id,top_title"
        columns = columns_str.split(",")
        columns.append('view_count')
        ses = my_db.sql_session()
        for channel_id in channel_id_list:
            """首页查询的结果将不会排除过期的话题／投票"""
            sql = "select {0},(select count(view_count.view_id) from view_count where " \
                  "topic_info.top_id=view_count.topic_id) from topic_info where can_show=1 " \
                  "and channel_id={1} " \
                  "order by create_date desc limit 0,5".format(columns_str, channel_id)
            proxy = ses.execute(sql)
            temp = proxy.fetchall()
            result = [dict(zip(columns, x)) for x in temp]
            index_topic_dict[channel_id] = result
        ses.close()
        """将字典按照左右两列排序，以帖子被浏览总数降序排列"""
        pass
        cache.set(key, index_topic_dict, timeout=60 * 1)

    return index_topic_dict
