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
    value = redis_client.get("user_info_columns")
    if value is None or first:
        sql = "SHOW columns FROM user_info"
        session = my_db.sql_session()
        proxy_result = session.execute(sql)
        session.close()
        result = proxy_result.fetchall()
        value = json.dumps([x[0] for x in result]).encode()
        redis_client.set('user_info_columns', value)
    return json.loads(value.decode())


get_columns(True)  # 第一次启动时加载


def get_sign(born_date):
    """根据日期获取星座，日期是2012-12-12 这样格式的字符串"""
    sign_dict = {(12, 21): "摩羯", (11, 23): "射手", (10, 24): "天蝎", (9, 23): "天秤", (8, 23): "处女",
                 (7, 23): "狮子", (6, 22): "巨蟹", (5, 21): "双子", (4, 20): "金牛", (3, 21): "白羊",
                 (2, 19): "双鱼", (1, 20): "水瓶"}
    sign = None
    try:
        date = datetime.datetime.strptime(born_date, "%Y-%m-%d")
        month = date.month
        day = date.day
        md = (month, day)
        key_list = [x for x in sign_dict.keys()]
        key_list.sort(key=lambda obj: (obj[0], obj[1]), reverse=True)
        for x in key_list:
            if md[0] == x[0]:
                """匹配月份"""
                if md[1] >= x[1]:
                    """那就是这个x对应的星座"""
                    return sign_dict[x]
                else:
                    """否则就是上一个月对应的星座"""
                    temp_index = key_list.index(x) + 1
                    temp_index = 0 if temp_index == 12 else temp_index
                    return sign_dict[key_list[temp_index]]
    except TypeError as e:
        print(e)
        print("出生日期类型错误")
    except ValueError:
        print("出生日期格式错误")
    return sign


def check_user_args(**kwargs):
    """检查对user_info进行操作的参数，防止sql注入"""
    flag = True
    msg = None
    columns = get_columns()
    for k, v in kwargs.items():
        if k not in columns:
            """有多余的参数"""
            flag = False
            msg = ("有多余的参数")
            break
        elif k == 'user_born_date' or k == "user_address":
            result = my_db.validate_arg(v, "-")
            if not result:
                flag = result
                msg = ("user_born_date 或 user_address 验证失败")
                print("user_born_date 或 user_address 验证失败")
                break
        elif k == "create_date":
            result = my_db.validate_arg(v, "-:")
            if not result:
                flag = result
                msg = ("create_date 验证失败")
                print("create_date 验证失败")
                break
        elif k == "user_phone":
            result = my_db.check_phone(v)
            if not result:
                flag = result
                msg = ("user_phone 验证失败")
                print("user_phone 验证失败")
                break
        elif k == "user_nickname":
            result = my_db.validate_arg(v, "_")
            if not result:
                flag = result
                msg = ("user_nickname 验证失败")
                print("user_nickname 验证失败")
                break
        elif k == "user_realname":
            result = my_db.validate_arg(v, ".")
            if not result:
                flag = result
                msg = ("user_realname 验证失败")
                print("user_realname 验证失败")
                break
        elif k == "user_img_url":
            result = my_db.validate_arg(v, "._/-")
            if not result:
                flag = result
                msg = ("user_img_url 验证失败")
                print("user_img_url 验证失败")
                break
        elif k == "user_mail":
            result = my_db.validate_arg(v, "._@-")
            if not result:
                flag = result
                msg = ("user_mail 验证失败")
                break
        elif k == "user_open_id":
            result = my_db.validate_arg(v, "-")
            if not result:
                flag = result
                msg = ("user_open_id 验证失败")
                break
        else:
            result = my_db.validate_arg(v)
            if not result:
                flag = result
                break
    return flag, msg


def add_user(**kwargs):
    """增加用户,参数必须是键值对的形式,注意，暂时没追加微信登录的方式"""
    message = {"message": "success"}
    flag, msg = check_user_args(**kwargs)
    if not flag:
        message["message"] = "参数错误 %s"%(msg)
    else:
        for k, v in kwargs.items():
            if k == "user_phone" and check_phone_registered(v):
                message["message"] = "phone registered"
                return message
        try:
            sql = my_db.structure_sql("add", "user_info", **kwargs)
            session = my_db.sql_session()
            session.execute(sql)
            session.commit()
        except sqlalchemy.exc.IntegrityError as e1:
            """
            re.findall(r"for key '(.+?)'",str) 是从str中找到匹配以for key 'PRIMARY'")
            句子中的PRIMARY,findall方法返回的是数组
            """
            print(e1.args)
            error_cause = re.findall(r"for key '(.+?)'", e1.args[-1])[0]
            if error_cause == "user_phone":
                message["message"] = "此手机已注册过"
            elif error_cause == "PRIMARY":
                message["message"] = "用户ID重复"
            else:
                print(error_cause)
                message['message'] = "注册失败，请联系客服"
        except Exception as e2:
            print(e2)
            print("未知错误")
        finally:
            session.close()
    return message


def edit_user(**kwargs):
    """修改用户资料,参数必须是键值对的形式"""
    message = {"message": "success"}
    flag , msg = check_user_args(**kwargs)
    if not flag:
        message["message"] = "参数错误%s"%(msg)
    else:
        user_id = kwargs.pop("user_id", None)
        if user_id is None or len(user_id) != 20:
            message["message"] = "无效的用户ID"
        else:
            sql = my_db.structure_sql("edit", "user_info", query_terms="where user_id='{}'".format(user_id), **kwargs)
            session = my_db.sql_session()
            try:
                session.execute(sql)
                session.commit()
            except Exception as e:
                print(e)
                message['message'] = '编辑用户信息失败'
            finally:
                session.close()
    return message


def change_status(the_type, user_id):
    """启用/禁用/删除账户 ,第一个参数是up/down/delete ，启用或者禁用，第二个是用户id"""
    message = {"message": "success"}
    if my_db.validate_arg(user_id) and my_db.validate_arg(the_type):
        if the_type.strip().lower() == "up":
            verb = "启用"
            sql = "update user_info set user_status=1 where user_id='{}'".format(user_id)
        elif the_type.strip().lower() == "delete":
            verb = "删除"
            sql = "delete from user_info where user_id='{}'".format(user_id)
        else:
            verb = "禁用"
            sql = "update user_info set user_status=0 where user_id='{}'".format(user_id)
        session = my_db.sql_session()
        try:
            session.execute(sql)
            session.commit()
        except Exception as e:
            print(e)
            message['message'] = "{}账户失败".format(verb)
        finally:
            session.close()
    else:
        message['message'] = "用户ID错误"
    return message


def login_phone(user_phone, user_password):
    """用手机登录"""
    message = {"message": "success"}
    if my_db.check_phone(user_phone) and my_db.validate_arg(user_password):
        session = my_db.sql_session()
        columns = get_columns()
        sql = "select " + ",".join(columns) + " from user_info where user_phone='{}'".format(user_phone)
        try:
            proxy_result = session.execute(sql)
            result = proxy_result.fetchone()
            if result is None:
                message['message'] = "此手机号码还未注册"
            else:
                result = my_db.str_format(result)
                result = dict(zip(columns, result))
                if user_password.lower() == result['user_password'].lower():
                    if result['user_status'] == 1:
                        message['data'] = result
                    else:
                        message['message'] = "此账户已冻结"
                else:
                    message["message"] = "密码错误"
        except Exception as e:
            print(e)
            message['message'] = '查询失败'
        finally:
            session.close()
    else:
        message['message'] = "参数错误"
    return message


def login_wx(open_id, union_id):
    """用户微信登录"""
    pass


def user_login(the_type='phone', **kwargs):
    """登录的总方法，回区分登录方式，如果是phone，就是手机登录，需要user_phone和
    user_password，如果是wx，那就是微信登录，需要open_id, uncon_id"""
    if the_type == "phone":
        return login_phone(kwargs.get("user_phone"), kwargs.get("user_password"))
    elif the_type == "wx":
        return login_wx(kwargs.get("open_id"), kwargs.get("union_id"))
    else:
        return {"message": "未知登录方式"}


def get_user_info(user_id, user_password):
    """根据用户id和密码获取信息"""
    message = {"message": "success"}
    if my_db.validate_arg(user_password) and my_db.validate_arg(user_password):
        session = my_db.sql_session()
        columns = get_columns()
        sql = "select " + ",".join(columns) + " from user_info where user_id='{}'".format(user_id)
        try:
            proxy_result = session.execute(sql)
            result = proxy_result.fetchone()
            if result is None:
                message['message'] = "此ID不存在"
            else:
                result = my_db.str_format(result)
                result = dict(zip(columns, result))
                if user_password.lower() == result['user_password'].lower():
                    if result['user_status'] == 1:
                        message['data'] = result
                    else:
                        message['message'] = "账户已冻结"
                else:
                    message["message"] = "密码错误"
        except Exception as e:
            print(e)
            message['message'] = '查询失败'
        finally:
            session.close()
    else:
        message['message'] = "参数错误"
    return message


def check_phone_registered(phone):
    """查看手机号是否被注册"""
    session = my_db.sql_session()
    columns = get_columns()
    sql = "select " + ",".join(columns) + " from user_info where user_phone='{}'".format(phone)
    try:
        proxy_result = session.execute(sql)
        result = proxy_result.fetchone()
        if result is None:
            return False
        else:
            return True
    except Exception as e:
        return True
    finally:
        session.close()


def check_wx(user_open_id):
    """根据用户微信id和密码获取信息"""
    message = {}
    session = my_db.sql_session()
    columns = get_columns()
    sql = "select " + ",".join(columns) + " from user_info where user_open_id='{}'".format(user_open_id)
    try:
        proxy_result = session.execute(sql)
        result = proxy_result.fetchone()
        if result is None:
            message['message'] = "not exists"
        else:
            result = my_db.str_format(result)
            result = dict(zip(columns, result))
            if result['user_status'] == 1:
                message["message"] = "exists"
                message['data'] = result
            else:
                message['message'] = "账户已冻结"
    except Exception as e:
        print(e)
        message['message'] = 'fail'
    finally:
        session.close()
    return message


def check_id(user_id, user_password):
    """检查用户身份，用于在身份验证装饰器"""
    return get_user_info(user_id, user_password)


def user_count(available=True):
    """统计所有用户的数量，available参数表示是否统计被禁用的账户，默认为统计
    返回int对象
    """
    redis_client = my_db.MyRedis.redis_client()
    result = redis_client.get("user_count")
    if not result:
        session = my_db.sql_session()
        if available:
            sql = "select count(1) from user_info"
        else:
            sql = "select count(1) from user_info where user_status=1"
        try:
            proxy_result = session.execute(sql)
            result = proxy_result.fetchone()[0]
        finally:
            session.close()
            redis_client.set("user_count", result, ex=5*60)
    else:
        result = int(result)
    return result


def page(index=1, length=30):
    """分页查询用户，后台管理用，index是页码，length是每页多少条记录"""
    message = {"message": "success"}
    if isinstance(index, (int, str)) and isinstance(length, (int, str)):
        try:
            index = index if isinstance(index, int) else int(index)
            length = length if isinstance(length, int) else int(length)
            session = my_db.sql_session()
            columns = get_columns()
            sql = "select " + ",".join(columns) + (" from user_info order by create_date desc "
                                                   "limit {},{}".format((index - 1) * length, length))
            try:
                proxy_result = session.execute(sql)
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
            finally:
                session.close()
        except TypeError:
            message['message'] = "参数错误"
    else:
        raise TypeError("参数只能是str或者int")
        message['message'] = "参数类型错误"
    return message


# print(page(1, 30))
# print(login("15618317376", ""))
# print(add_user(user_id='20121457894123456279',user_phone='15618311366',user_password="",create_date='2917-01-01'))
# print(edit_user(user_id='20121457894123456789',user_phone='15618317376',user_password="12",create_date='2917-01-01'))
# print(change_status("delete",'20121457894123456789'))
