# -*- coding:utf8 -*-
import my_db
import sqlalchemy.exc
import json
from threading import RLock
import re
"""投票计数"""


def get_columns(first=False):
    """获取所有的topic_info表的列名，只在启动程序时运行一次,参数
    first是代表是否第一次启动，如果第一次启动要强制重新加载列名"""
    redis_client = my_db.MyRedis.redis_client()
    value = redis_client.get("vote_count_columns")
    if value is None or first:
        sql = "SHOW columns FROM vote_count"
        session = my_db.sql_session()
        proxy_result = session.execute(sql)
        session.close()
        result = proxy_result.fetchall()
        value = json.dumps([x[0] for x in result]).encode()
        redis_client.set('vote_count_columns', value)
    return json.loads(value.decode())


def add_vote_cache(topic_id, support_a, support_b):
    """用户投票时，对缓存中的数据进行操作"""
    cache = my_db.cache
    key = "vote_count_{}".format(topic_id)
    result = cache.get(key)
    if support_a:
        result['support_a'] += 1
    if support_b:
        result['support_b'] += 1
    cache.set(key, result, timeout=60*60*12)


def vote(**kwargs):
    """投票计数"""
    message = {"message": "success"}
    kwargs['create_date'] = my_db.current_datetime()
    sql = my_db.structure_sql("add", "vote_count", **kwargs)
    sql_session = my_db.sql_session()
    try:
        sql_session.execute(sql)
        sql_session.commit()
        """同步道缓存"""
        lock = RLock()
        lock.acquire()
        # 设置投票计数缓存
        add_vote_cache(kwargs['topic_id'], kwargs['support_a'], kwargs['support_b'])
        lock.release()
        support = "b" if str(kwargs['support_a']) == "0" else "a"
        set_voted_cache(kwargs['only_id'], kwargs['topic_id'], support)  # 设置已投票缓存
    except sqlalchemy.exc.IntegrityError as e1:
        """
        re.findall(r"for key '(.+?)'",str) 是从str中找到匹配以for key 'PRIMARY'")
        句子中的PRIMARY,findall方法返回的是数组
        """
        print(e1.args)
        error_cause = re.findall(r"for key '(.+?)'", e1.args[-1])[0]
        if error_cause == "only_once":
            message["message"] = "你已经投过票了"
        else:
            print(error_cause)
            message['message'] = "投票失败，请联系管理员"
    finally:
        sql_session.close()
    return message


def __get_vote_count(topic_id):
    """低级方法。根据话题id获取相关的投票人数"""
    message = {'message': "success"}
    sql = "select sum(vote_count.support_a),sum(vote_count.support_b) from vote_count " \
          "where vote_count.topic_id='{}'".format(topic_id)
    ses = my_db.sql_session()
    proxy = ses.execute(sql)
    result = list(proxy.fetchone())
    result = [(0 if x is None else x) for x in result]
    ses.close()
    message['support_a'] = result[0]
    message['support_b'] = result[1]
    return message


def get_vote_count(topic_id, from_db=False):
    """高级方法。根据话题id获取相关的投票人数,返回的是字典，可以分别查看双方的支持人数"""
    message = {'message': "success"}
    cache = my_db.cache
    result = cache.get("vote_count_{}".format(topic_id))
    if result is None or from_db:
        result = __get_vote_count(topic_id)
        result.pop('message')
        cache.set("vote_count_{}".format(topic_id), result, timeout=60*60*12)
    message.update(result)
    return message


def sum_vote_count(topic_id):
    """统计一个话题的参与人数，返回ｉｎｔ"""
    result = get_vote_count(topic_id)
    if result['support_a'] is None or result['support_b'] is None:
        result = __get_vote_count(topic_id)
    return result['support_a'] + result['support_b']


def __get_view_count(topic_id):
    """低级，根据话题id获取话题的浏览人数"""
    sql = "select count(1) from view_count where topic_id='{}'".format(topic_id)
    ses = my_db.sql_session()
    proxy = ses.execute(sql)
    result = proxy.fetchone()[0]
    ses.close()
    return result


def get_view_count(topic_id):
    """高级，根据话题id获取话题的浏览人数"""
    cache = my_db.cache
    result = cache.get("view_count_{}".format(topic_id))
    if result is None:
        result = __get_view_count(topic_id)
        cache.set("view_count_{}".format(topic_id), result, timeout=60*60*12)
    return result


def __add_view_count(topic_id, only_id, from_ip, browser_type):
    """低级方法。对页面浏览进行计数"""
    message = {'message': "success"}
    sql = "insert into view_count(topic_id,only_id,from_ip,browser_type,create_date) " \
          "values('{0}','{1}','{2}','{3}','{4}')".format(topic_id, only_id, from_ip,
                                                         browser_type, my_db.current_datetime())
    ses = my_db.sql_session()
    ses.execute(sql)
    ses.commit()
    ses.close()
    return message


def set_voted_cache(only_id, topic_id, support=''):
    """设置是否已投票缓存"""
    cache = my_db.cache
    key = "voted_{}".format(only_id)
    temp_dict = cache.get(key)
    if temp_dict is None:
        if isinstance(topic_id, dict):
            """从数据库读出来的情况，批量添加，一般是topic_id为key，a/b为值的字典"""
            cache.set(key, topic_id, timeout=60 * 60 * 2)
        else:
            """单独添加一条记录"""
            cache.set(key, {topic_id: support}, timeout=60 * 60 * 2)
    else:
        temp_dict[topic_id] = support
        cache.set(key, temp_dict, timeout=60 * 60 * 2)


def get_voted_cache(only_id, topic_id):
    """从缓存中取是否已投票数据"""
    cache = my_db.cache
    key = "voted_{}".format(only_id)
    result = cache.get(key)
    if result is None:
        return 0  # 代表没有初始化
    else:
        result = result.get(topic_id)
        if result is not None:
            return result  # 已经初始化，并找到对应的投票记录
        else:
            return -1  # 已经初始化，但数组是空的


def is_voted(only_id, topic_id, from_db=False):
    """根据唯一性id和话题id判断此用户是否投过票了，返回字符串，a，b ，或者空字符，空字符代表没有投过票"""
    result = get_voted_cache(only_id, topic_id)
    if result == 0 or not from_db:
        ses = my_db.sql_session()
        sql = "select topic_id,support_a,support_b from vote_count where only_id='{}'".format(only_id)
        proxy = ses.execute(sql)
        result = proxy.fetchall()
        result = {x[0]: ("b" if x[1] == 0 else "a") for x in result}
        set_voted_cache(only_id, result)
        result = result.get(topic_id)
        if result is not None:
            return result
        else:
            return ''
    elif result == -1:
        return ''
    else:
        return result


def add_view_count(topic_id, only_id, from_ip, browser_type):
    """高级方法。对页面浏览进行计数,返回ｉｎｔ"""
    lock = RLock()
    cache = my_db.cache
    count = get_view_count(topic_id)
    lock.acquire()
    cache.set("view_count_{}".format(topic_id), count+1, timeout=60*60*12)
    lock.release()
    result = __add_view_count(topic_id, only_id, from_ip, browser_type)
    return result