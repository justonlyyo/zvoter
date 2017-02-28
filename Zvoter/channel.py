# -*- coding:utf8 -*-
import my_db

"""频道和类别"""


def set_cache(key, value, timeout=0):
    """把对象存入缓存"""
    cache = my_db.cache
    cache.set(key, value, timeout=timeout)


def get_cache(key):
    """从缓存取出数据"""
    return my_db.cache.get(key)


def get_channel():
    """获取所有频道,低级方法"""
    channel_sql = "SELECT channel_id,channel_name,channel_img_url FROM channel_info"
    sql_session = my_db.sql_session()
    proxy_result = sql_session.execute(channel_sql)
    channel_result = proxy_result.fetchall()
    sql_session.close()
    if len(channel_result) == 0:
        channel_dict = dict()
    else:
        channel_dict = [{"channel_id": x[0],
                         "channel_name": x[1],
                         "channel_img_url": x[2]} for x in channel_result]
    set_cache("channel_list", channel_dict)
    return channel_dict


def channel_list(from_db=False):
    """获取所有的频道信息，高级方法。from_db代表是否直接从数据读读取
    返回频道字典的数组。类似如下格式：
    ['channel_name': '财经', 'channel_img_url': 'icon_finance.png', 'channel_id': 3},.....]
    """
    if from_db:
        return get_channel()
    else:
        data = get_cache('channel_list')
        if data is None:
            data = get_channel()
        return data


def get_class():
    """获取所有小类,低级方法"""
    class_sql = "SELECT class_id,class_name,channel_id FROM class_info"
    sql_session = my_db.sql_session()
    proxy_result = sql_session.execute(class_sql)
    class_result = proxy_result.fetchall()
    sql_session.close()
    a_dict = dict()
    if len(class_result) == 0:
        pass
    else:
        for x in class_result:
            channel_id = x[2]
            class_obj = {"class_id": x[0], "class_name": x[1]}
            if channel_id in a_dict.keys():
                a_dict[channel_id].append(class_obj)
            else:
                a_dict[channel_id] = [class_obj]

    set_cache("small_class_dict", a_dict)
    return a_dict


def get_class_dict(from_db=False):
    """获取所有的小类信息，高级方法。from_db代表是否直接从数据读读取返回的是以channel_id为ｋｅｙ的字典"""
    if from_db:
        return get_class()
    else:
        data = get_cache('small_class_dict')
        if data is None:
            data = get_class()
        return data


def get_class_list():
    """获取所有的小类信息，高级方法。from_db代表是否直接从数据读读取返回的是以
    [{"class_id":class_id,"class_name:class_name},'...]这样字典的数组
    """
    cache = my_db.cache
    key = "small_class_list"
    data = cache.get(key)
    if data is None:
        sql = "SELECT class_id,class_name FROM class_info"
        ses = my_db.sql_session()
        proxy = ses.execute(sql)
        result = proxy.fetchall()
        ses.close()
        data = [dict(zip(['class_id', 'class_name'], x)) for x in result]
        cache.set(key, data, timeout=60*15)
    return data


def channel_and_class(flag1=False, flag2=False):
    """获取所有的频道和列别信息"""
    message = {"message": "success", "channel_list": channel_list(flag1), "small_class_dict": get_class_dict(flag2)}
    return message


def save_channel(channel_dict):
    """保存频道信息"""
    new_dict = channel_dict
    if new_dict:
        sql_session = my_db.sql_session()()
        for k, v in new_dict:
            sql = my_db.structure_sql("edit", "channel_info", "where channel_id={}".format(k), channel_name=v)
            sql_session.execute(sql)
        sql_session.commit()
        sql_session.close()
        return True
    else:
        raise ValueError("频道信息错误")
        return False


def save_class(small_class_dict):
    """保存类别信息,目前只能增加和修改，不能删除类别"""
    old_dict_raw = get_cache("small_class_dict")
    new_dict = small_class_dict
    add_list = list()  # 存放插入的小类的数组
    update_list = list()  # 存放更新的小类的数组
    drop_list = list()  # 存放删除的小类的id的数组
    old_list = []
    for k, v in old_dict_raw.items():
        for i in v:
            temp = {"channel_id": k, "class_id": i['class_id'], "class_name": i['class_name']}
            old_list.append(temp)
    new_list = [{"channel_id": new_dict[key]['channel_id'], "class_id": new_dict[key]['class_id'],
                 "class_name": key}
                for key in new_dict.keys()]
    if len(new_list) == 0:
        return {"message": "success"}
    else:
        new_keys = [x['class_id'] for x in new_list]
        drop_list = [x['class_id'] for x in old_list if str(x['class_id']) not in new_keys]
        old_keys = [x['class_id'] for x in old_list]
        for x in new_list:
            if x['class_id'] == "":
                add_list.append(x)
            else:
                update_list.append(x)
        sql_session = my_db.sql_session()
        if len(drop_list) > 0:
            for x in drop_list:
                sql = my_db.structure_sql("delete", "class_info", "where class_id={}".format(x))
                sql_session.execute(sql)
            sql_session.commit()
        if len(update_list) > 0:
            for x in update_list:
                class_id = x.pop("class_id")
                sql = my_db.structure_sql("edit", "class_info", "where class_id={}".format(class_id), **x)
                sql_session.execute(sql)
            sql_session.commit()
        if len(add_list) > 0:
            for x in add_list:
                x.pop("class_id")
                sql = my_db.structure_sql("add", "class_info", **x)
                sql_session.execute(sql)
            sql_session.commit()
        sql_session.close()
        return {"message": "success"}


