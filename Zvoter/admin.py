# -*- coding:utf8 -*-
import my_db
import sqlalchemy.exc
import datetime
import re
import json


def get_columns(first=False):
    """获取所有的admin_info表的列名，只在启动程序时运行一次,参数
    first是代表是否第一次启动，如果第一次启动要强制重新加载列名"""
    redis_client = my_db.MyRedis.redis_client()
    value = redis_client.get("admin_info_columns")
    if value is None or first:
        sql = "SHOW columns FROM admin_info"
        session = my_db.sql_session()
        proxy_result = session.execute(sql)
        session.close()
        result = proxy_result.fetchall()
        value = json.dumps([x[0] for x in result]).encode()
        redis_client.set('admin_info_columns', value)
    return json.loads(value.decode())


get_columns(True)  # 第一次启动时加载


def check_admin_args(**kwargs):
    """检查对admin_info进行操作的参数，防止sql注入"""
    flag = True
    columns = get_columns()
    for k, v in kwargs.items():
        if k not in columns:
            """有多余的参数"""
            flag = False
            break
        elif k == "create_date":
            result = my_db.validate_arg(v, "-:")
            if not result:
                flag = result
                break
        elif k == "admin_phone":
            result = my_db.check_phone(v)
            if not result:
                flag = result
                break
        elif k == "admin_name":
            result = my_db.validate_arg(v, "_")
            if not result:
                flag = result
                break
        elif k == "admin_mail":
            result = my_db.validate_arg(v, "._-@")
            if not result:
                flag = result
                break
        else:
            result = my_db.validate_arg(v)
            if not result:
                flag = result
                break
    return flag


def add_admin(**kwargs):
    """增加管理员,参数必须是键值对的形式,"""
    message = {"message": "success"}
    if not check_admin_args(**kwargs):
        message["message"] = "参数错误"
    else:
        try:
            sql = my_db.structure_sql("add", "admin_info", **kwargs)
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
            if error_cause == "admin_phone":
                message["message"] = "管理员手机重复"
            else:
                print(error_cause)
                message['message'] = "添加管理员失败"
        except Exception as e2:
            print(e2)
            print("未知错误")
        finally:
            session.close()
    return message


def edit_admin(**kwargs):
    """修改管理员资料,参数必须是键值对的形式"""
    message = {"message": "success"}
    if not check_admin_args(**kwargs):
        message["message"] = "参数错误"
    else:
        admin_id = kwargs.pop("admin_id", None)
        if admin_id is None or not my_db.validate_arg(admin_id):
            message["message"] = "无效的用户ID"
        else:
            sql = my_db.structure_sql("edit", "admin_info", query_terms="where admin_id='{}'".format(admin_id), **kwargs)
            session = my_db.sql_session()
            try:
                session.execute(sql)
                session.commit()
            except Exception as e:
                print(e)
                message['message'] = '编辑管理员信息失败'
            finally:
                session.close()
    return message


def change_status(the_type, admin_id):
    """启用/禁用/删除管理员账户 ,第一个参数是up/down/delete ，启用或者禁用，第二个是用户id"""
    message = {"message": "success"}
    if my_db.validate_arg(admin_id) and my_db.validate_arg(the_type):
        if the_type.strip().lower() == "up":
            verb = "启用"
            sql = "update admin_info set admin_status=1 where admin_id='{}'".format(admin_id)
        elif the_type.strip().lower() == "delete":
            verb = "删除"
            sql = "delete from admin_info where admin_id='{}'".format(admin_id)
        else:
            verb = "禁用"
            sql = "update admin_info set admin_status=0 where admin_id='{}'".format(admin_id)
        session = my_db.sql_session()
        try:
            session.execute(sql)
            session.commit()
        except Exception as e:
            print(e)
            message['message'] = "{}管理员失败".format(verb)
        finally:
            session.close()
    else:
        message['message'] = "管理员ID错误"
    return message


def login(admin_name, admin_password):
    """管理员登录"""
    message = {"message": "success"}
    if my_db.validate_arg(admin_name) and my_db.validate_arg(admin_password):
        session = my_db.sql_session()
        columns = get_columns()
        sql = "select " + ",".join(columns) + " from admin_info where admin_name='{}'".format(admin_name)
        try:
            proxy_result = session.execute(sql)
            result = proxy_result.fetchone()
            if result is None:
                message['message'] = "管理员账户不存在"
            else:
                result = my_db.str_format(result)
                result = dict(zip(columns, result))
                if admin_password.lower() == result['admin_password'].lower():
                    if result['admin_status'] == 1:
                        message['data'] = result
                    else:
                        message['message'] = "此管理员账户已禁用"
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


def get_admin_info(admin_id, admin_password):
    """根据管理员id和密码获取信息"""
    message = {"message": "success"}
    try:
        admin_id = int(admin_id)
    except ValueError:
        pass
    finally:
        pass
    if admin_id and my_db.validate_arg(admin_password):
        session = my_db.sql_session()
        columns = get_columns()
        sql = "select " + ",".join(columns) + " from admin_info where admin_id='{}'".format(admin_id)
        try:
            proxy_result = session.execute(sql)
            result = proxy_result.fetchone()
            if result is None:
                message['message'] = "此ID不存在"
            else:
                result = my_db.str_format(result)
                result = dict(zip(columns, result))
                if admin_password.lower() == result['admin_password'].lower():
                    if result['admin_status'] == 1:
                        message['data'] = result
                    else:
                        message['message'] = "此管理员账户已禁用"
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


def check_admin_id(admin_id, admin_password):
    """检查管理员身份，用于在身份验证装饰器"""
    return get_admin_info(admin_id, admin_password)


def admin_count():
    """统计管理员数量
    返回int对象
    """
    redis_client = my_db.MyRedis.redis_client()
    result = redis_client.get("admin_count")
    if not result:
        session = my_db.sql_session()
        sql = "select count(1) from admin_info"
        try:
            proxy_result = session.execute(sql)
            result = proxy_result.fetchone()[0]
        finally:
            session.close()
            redis_client.set("admin_count", result, ex=10*60)
    else:
        result = int(result)
    return result


def page(index=1, length=30):
    """分页查询管理员，后台管理用，index是页码，length是每页多少条记录"""
    message = {"message": "success"}
    if isinstance(index, (int, str)) and isinstance(length, (int, str)):
        try:
            index = index if isinstance(index, int) else int(index)
            length = length if isinstance(length, int) else int(length)
            session = my_db.sql_session()
            columns = get_columns()
            sql = "select " + ",".join(columns) + (" from admin_info order by create_date desc "
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



