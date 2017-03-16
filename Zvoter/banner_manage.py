# -*- coding:utf8 -*-
import my_db
import random

"""banner管理"""

cache = my_db.cache
column_str = "banner_id,banner_url,banner_alt,order_index"


class FromDB:
    """单例模式，确认是否从数据库加载"""

    def __init__(self):
        pass

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            obj = super(FromDB, cls).__new__(cls)
            obj.__flag = dict()  # 是否从数据库加载的标志位
            obj.__sn = random.random()
            cls.instance = obj
        return cls.instance

    @classmethod
    def no(cls, key_word):
        """设置不从数据库加载"""
        obj = FromDB()
        try:
            obj.__flag.pop(key_word)
        except KeyError:
            pass

    @classmethod
    def yes(cls, key_word):
        """设置从数据库加载"""
        obj = FromDB()
        obj.__flag[key_word] = 1

    @classmethod
    def from_db(cls, key_word):
        """检测是否需要从数据库加载,检测后自动设置from_db为False"""
        obj = FromDB()
        result = None
        try:
            result = obj.__flag.pop(key_word)
        except KeyError:
            pass
        return result


def __get_banner():
    """低级方法从数据库查询所有的banner配置信息,返回字典的数组"""
    sql = "select {} from banner_info order by order_index".format(column_str)  # 以人工排序
    ses = my_db.sql_session()
    proxy = ses.execute(sql)
    result = proxy.fetchall()
    columns = column_str.split(",")
    result = [dict(zip(columns, x)) for x in result]
    ses.close()
    return result


def get_banner():
    """高级方法，从数据库查询所有的banner配置信息,返回字典的数组"""
    if not FromDB.from_db("banner_info"):
        result = cache.get("banner_list")
        if result is None:
            result = __get_banner()
            cache.set("banner_list", result, timeout=60 * 60 * 2)
    else:
        result = __get_banner()
        cache.set("banner_list", result, timeout=60 * 60 * 2)

    return result


def manage_banner(**kwargs):
    """对banner的add，delete和edit"""
    message = {"message": "success"}
    ses = my_db.sql_session()
    try:
        the_type = kwargs.pop('the_type')
        if the_type == "add":
            banner_url = 'banner1.png' if kwargs.get('banner_url') is None else kwargs.get('banner_url')
            banner_alt = '' if kwargs.get('banner_alt') is None else kwargs.get('banner_alt')
            order_index = '1' if kwargs.get('order_index') is None else kwargs.get('order_index')
            order_index = int(order_index) if order_index.isdigit() else 1
            sql = "insert into banner_info(banner_url,banner_alt,order_index) values('{}','{}',{})".\
                format(banner_url, banner_alt, order_index)
            ses.execute(sql)
            ses.commit()
        elif the_type == 'delete':
            try:
                banner_id = kwargs['banner_id']
                try:
                    banner_id = int(banner_id)
                    sql = 'select banner_id from banner_info'
                    proxy = ses.execute(sql)
                    result = [x[0] for x in proxy.fetchall()]
                    if banner_id not in result:
                        message['message'] = '错误的id'
                    else:
                        sql = "delete from banner_info where banner_id={}".format(banner_id)
                        ses.execute(sql)
                        ses.commit()
                except ValueError:
                    raise ValueError("待删除id格式错误")
                    message['message'] = '待删除id格式错误'
            except KeyError:
                raise KeyError("删除banner没有找到banner_id")
                message['message'] == '待删除id无效'
        elif the_type == 'edit':
            banner_id = kwargs.get('banner_id')
            if banner_id is None:
                message['message'] = '没有banner_id'
            else:
                if banner_id.isdigit():
                    banner_id = int(banner_id)
                    banner_url = 'banner1.png' if kwargs.get('banner_url') is None else kwargs.get('banner_url')
                    banner_alt = '' if kwargs.get('banner_alt') is None else kwargs.get('banner_alt')
                    order_index = '1' if kwargs.get('order_index') is None else kwargs.get('order_index')
                    order_index = int(order_index) if order_index.isdigit() else 1

                    sql = "update banner_info set banner_url='{}',banner_alt='{}',order_index={} where banner_id={}".\
                        format(banner_url, banner_alt, order_index, banner_id)
                    ses.execute(sql)
                    ses.commit()
                else:
                    message['message'] = 'id非法'

    except KeyError:
        raise KeyError("the_type参数不存在")
        message['message'] = '操作类型错误'
    finally:
        ses.close()
        FromDB.yes("banner_info")  # 提醒要从数据库重新加载banner数据,参数为表明
        return message


def get_keywords(channel_id="0"):
    """根据频道获取对应的搜索热词，keywords,title,description,channel_id=0代表首页"""
    if channel_id is None:
        raise KeyError("频道id缺失")
    else:
        channel_id = str(channel_id)
        if channel_id.isdigit() or channel_id == "all":
            column_text = "key_word_id,channel_id,word_type,word_text"
            columns = column_text.split(",")
            cache_key = "keywords_{}".format(channel_id)
            result = cache.get(cache_key)
            if result is None or FromDB.from_db("key_word_info"):
                ses = my_db.sql_session()
                if channel_id == "all":
                    """all是不包含首页的关键词设置的，请注意"""
                    sql = "select {} from key_word_info where channel_id!=0".format(column_text)
                    proxy = ses.execute(sql)
                    datas = proxy.fetchall()
                    channel_id_list = set([x['channel_id'] for x in datas])
                    result = dict(zip(channel_id_list, [[] for x in range(len(channel_id_list))]))
                    temp_list = [dict(zip(columns, x)) for x in datas]
                    for x in temp_list:
                        result[x['channel_id']].append(x)  # 返回的是字典的数组的字典
                else:
                    sql = "select {} from key_word_info where channel_id={}".format(column_text, channel_id)
                    proxy = ses.execute(sql)
                    datas = proxy.fetchall()
                    temp_list = [dict(zip(columns, x)) for x in datas]
                    result = {x['word_type']: x for x in temp_list}  # 注意返回的类型是以word_type为key的字典
                cache.set(cache_key, result, timeout=60*60*2)
                ses.close()
            else:
                pass
            return result
        else:
            raise KeyError("频道id错误")


def manage_keywords(**kwargs):
    """对搜索热词，keywords,title,description的操作"""
    message = {"message": "success"}
    ses = my_db.sql_session()
    try:
        the_type = kwargs.pop('the_type')
        if the_type == "add":
            sql = my_db.structure_sql("add", 'key_word_info', kwargs)
            ses.execute(sql)
            ses.commit()
        elif the_type == 'delete':
            try:
                key_word_id = kwargs['key_word_id']
                try:
                    key_word_id = int(key_word_id)
                    sql = 'select key_word_id from key_word_info'
                    proxy = ses.execute(sql)
                    result = [x[0] for x in proxy.fetchall()]
                    if key_word_id not in result:
                        message['message'] = '错误的id'
                    else:
                        sql = "delete from key_word_info where key_word_id={}".format(key_word_id)
                        ses.execute(sql)
                        ses.commit()
                except ValueError:
                    raise ValueError("待删除id格式错误")
                    message['message'] = '待删除id格式错误'
            except KeyError:
                raise KeyError("删除key_word_info没有找到key_word_id")
                message['message'] == '待删除id无效'
        elif the_type == 'edit':
            key_word_id = kwargs.get('key_word_id')
            if key_word_id is None:
                message['message'] = '没有key_word_id'
            else:
                if key_word_id.isdigit():
                    adict = {k: v for k, v in kwargs.items() if v != "" or v is not None}
                    sql = my_db.structure_sql("edit", "key_word_info", "where key_word_id={}".format(key_word_id),
                                              **adict)
                    ses.execute(sql)
                    ses.commit()
                else:
                    message['message'] = 'id非法'

    except KeyError:
        raise KeyError("the_type参数不存在")
        message['message'] = '操作类型错误'
    finally:
        ses.close()
        FromDB.yes("key_word_info")  # 提醒要从数据库重新加载banner数据，参数为表明
        return message



