# -*- coding:utf8 -*-
import my_db
import json

"""留言管理模块"""


def manage_comment(**kwargs):
    """管理用户留言"""
    message = {"message": "success"}
    ses = my_db.sql_session()
    try:
        the_type = kwargs.pop("the_type")
        if the_type == "add":
            """添加留言"""
            kwargs['create_date'] = my_db.current_datetime()
            sql = my_db.structure_sql("add", "comment_info", **kwargs)
            ses.execute(sql)
            ses.commit()
        elif the_type == "edit":
            comment_id = kwargs.pop("comment_id")
            sql = my_db.structure_sql("edit", "comment_info", "where comment_id={}".format(comment_id), **kwargs)
            ses.execute(sql)
            ses.commit()
        elif the_type == 'delete':
            comment_id = kwargs.pop("comment_id")
            sql = my_db.structure_sql("delete", "comment_info", "where comment_id={}".format(comment_id), **kwargs)
            ses.execute(sql)
            ses.commit()
        elif the_type == "by_comment_id":
            """根据评论id获取话题"""
            comment_id = kwargs.pop("comment_id")
            child_sql = "(SELECT CONCAT_WS(' vs ',SUM(up_it),SUM(down))  " \
                        "FROM up_down_info WHERE up_down_info.comment_id=comment_info.comment_id)"  # 查询赞和踩的子查询
            column_str = "comment_id,comment_text,comment_author,user_info.user_nickname,user_info.user_img_url," \
                         "create_date,support_side,topic_id,parent_comment,comment_status,{}".format(child_sql)
            sql = "select {} from comment_info,user_info where comment_status>0  user_id=comment_author " \
                  "and comment_id={}".format(column_str, comment_id)
            proxy = ses.execute(sql)
            result = proxy.fetchone()
            columns = ['comment_id', 'comment_text', 'user_id', 'user_nickname', 'user_img_url', 'create_date',
                       'support_side',
                       'topic_id', 'parent_comment', 'comment_status', "up_vs_down"]
            """
            列名分别代表：评论id，评论内容,用户id，用户昵称，用户头像，发布时间，支持方向，话题id，评论状态
            被评论对象id，赞和踩的数量
            """
            if result is None:
                message['data'] = dict()
            else:
                message['data'] = dict(zip(columns, result))
        elif the_type == "by_topic_id":
            """根据话题id获取话题"""
            topic_id = kwargs.pop("topic_id")
            child_sql = "(SELECT CONCAT_WS(' vs ',SUM(up_it),SUM(down_it))  " \
                        "FROM up_down_info WHERE up_down_info.comment_id=comment_info.comment_id)"  # 查询赞和踩的子查询
            column_str = "comment_id,comment_text,comment_author,user_info.user_nickname,user_info.user_img_url," \
                         "comment_info.create_date,support_side,topic_id,parent_comment,comment_status,{}".\
                format(child_sql)
            sql = "select {} from comment_info,user_info where comment_status>0 and  user_id=comment_author " \
                  "and topic_id={}".format(column_str, topic_id)
            proxy = ses.execute(sql)
            result = proxy.fetchall()
            columns = ['comment_id', 'comment_text', 'user_id', 'user_nickname', 'user_img_url', 'create_date',
                       'support_side',
                       'topic_id', 'parent_comment', 'comment_status', "up_vs_down"]
            """
            列名分别代表：评论id，评论内容,用户id，用户昵称，用户头像，发布时间，支持方向，话题id，评论状态
            被评论对象id，赞和踩的数量
            """
            if len(result) == 0:
                message['data'] = list()
            else:
                result = [dict(zip(columns, x)) for x in result]
                message['data'] = result
        elif the_type == "all":
            """获取所有评论，用于后台管理"""
            topic_id = kwargs.pop("topic_id")
            child_sql = "(SELECT CONCAT_WS(' vs ',SUM(up_it),SUM(down))  " \
                        "FROM up_down_info WHERE up_down_info.comment_id=comment_info.comment_id)"  # 查询赞和踩的子查询
            column_str = "comment_id,comment_text,comment_author,user_info.user_nickname,user_info.user_img_url," \
                         "create_date,support_side,topic_id,parent_comment,comment_status,{}".format(child_sql)
            sql = "select {} from comment_info,user_info where user_id=comment_author " \
                  "and topic_id={}".format(column_str, topic_id)
            proxy = ses.execute(sql)
            result = proxy.fetchall()
            columns = ['comment_id', 'comment_text', 'user_id', 'user_nickname', 'user_img_url', 'create_date',
                       'support_side',
                       'topic_id', 'parent_comment', 'comment_status', "up_vs_down"]
            """
            列名分别代表：评论id，评论内容,用户id，用户昵称，用户头像，发布时间，支持方向，话题id，评论状态
            被评论对象id，赞和踩的数量
            """
            if len(result) == 0:
                message['data'] = list()
            else:
                message['data'] = [dict(zip(columns, x)) for x in result]
        elif the_type == "page":
            """分页查询所有评论"""
            index = kwargs.get("index")
            length = kwargs.get("page_length")
            try:
                index = int(index)
                length = int(length)
                columns = ['comment_id', 'comment_text', 'comment_author', 'comment_info.create_date',
                           'support_side', 'user_info.user_nickname', 'topic_id'
                           , 'topic_info.top_title', 'parent_comment', 'comment_status']
                sql = "select " + ",".join(columns) + (" from comment_info,user_info,topic_info where "
                                                       "topic_info.top_id=comment_info.topic_id and "
                                                       "user_id=comment_author order by create_date desc "
                                                       "limit {},{}".format((index - 1) * length, length))
                try:
                    columns = ['comment_id', 'comment_text', 'comment_author', 'create_date',
                               'support_side', 'user_nickname',
                               'topic_id', 'topic_title', 'parent_comment', 'comment_status']
                    proxy_result = ses.execute(sql)
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
        ses.close()
        return message


def comment_count():
    """统计所有评论的数量"""
    sql_session = my_db.sql_session()
    sql = "select count(1) from comment_info"
    proxy = sql_session.execute(sql)
    result = proxy.fetchone()[0]
    sql_session.close()
    return result
