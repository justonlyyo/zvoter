# -*- coding:utf8 -*-

from flask import Flask, request, render_template, make_response, flash, send_file
from flask_session import Session
from werkzeug.utils import secure_filename
import requests
from img_code import *
from flask import abort
from my_tools import *
import json
import os
import io
import channel
import math
import sys
import topic
import base64
import vote_tools

port = 5666  # 定义端口
app = Flask(__name__)

"""上传文件相关配置"""
upload_dir_path = sys.path[0] + os.sep + "static" + os.sep + 'upload' + os.sep + 'images'
if not os.path.exists(upload_dir_path):
    os.makedirs(upload_dir_path)
UPLOAD_FOLDER = upload_dir_path  # 后台上传图片上传的路径
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = ('png', 'jpg', 'jpeg', 'gif')  # 允许上传的图片后缀

"""主程序基础配置部分"""
session_key = os.urandom(24)
app.config.update({
    'SESSION_PERMANENT': False,  # 配置会话的生命期不是永久有效
    'PERMANENT_SESSION_LIFETIME': 60*30,  # session 闲置超时时间，秒
    "SECRET_KEY": session_key  # 配置session的密钥
})
SESSION_TYPE = 'redis'  # flask-session使用redis，注意必须安装redis数据库和对应的redis模块
app.config.from_object(__name__)  # flask-session相关
Session(app)  # flask-session相关


# cache = RedisCache()  # my_tools里面有，所以这里注销了。


def zone_info(the_type='list', the_arg=None):
    """the_type代表查询的类型，the_arg是查询用的关键字,是省市名称的代码"""
    key = "PCHBZ-NTKHF-6QYJB-JN7WD-IDX2T-5YFIK"
    url_children = "http://apis.map.qq.com/ws/district/v1/getchildren"
    the_arg = '310000' if not isinstance(the_arg, str) else the_arg
    result = None
    if the_type == "list":
        zone_list = cache.get("zone_list")
        if zone_list is None:
            r = requests.get(url_children + "?key=" + key)
            if r.status_code == 200:
                result = r.json().get("result")
                if result is not None:
                    result = {x["fullname"]: x["id"] for x in result[0]}
                    cache.set('zone_list', result, timeout=0)
            else:
                pass
        else:
            result = zone_list
    elif the_type == "children":
        info_name = "zone_info_" + the_arg
        zone_list_top = cache.get(info_name)
        if zone_list_top is None:
            r = requests.get(url_children + "?key=" + key + "&id=" + the_arg)
            if r.status_code == 200:
                result = r.json().get("result")
                if result is not None:
                    result = [x["fullname"] for x in result[0]]
                    cache.set(info_name, result, timeout=0)
            else:
                pass
        else:
            result = zone_list_top
    else:
        pass
    return result


@app.route('/index.html')
def index_page():
    return redirect(url_for("index"))


@app.route('/')
def index():
    """返回首页"""
    login_flag = is_login(session)  # 用户是否已登录
    channel_list = channel.channel_list()  # 频道列表
    channel_dict = {x['channel_id']: x['channel_name'] for x in channel_list}
    form = SearchLoginForm()  # 搜索from
    img_form = PhotoForm()  # 上传图片from
    index_dict = topic.index_topic_list()  # 首页帖子字典
    side_bar_list = topic.side_bar_topic_list()  # 侧边栏的列表
    if login_flag:
        try:
            user_img_url = session['user_img_url']
        except KeyError:
            user_img_url = ""
        # 用户头像
        user_img_url = '../static/image/guest.png' if user_img_url == "" else session['user_img_url']
        user_level = 1  # 用户级别，暂时替代
        return render_template("index.html", login_flag=login_flag, side_bar_list=side_bar_list,
                               user_img_url=user_img_url, user_level=user_level,
                               channel_list=channel_list, channel_dict=channel_dict,
                               form=form, img_form=img_form, index_dict=index_dict)
    else:
        return render_template("index.html", login_flag=login_flag, channel_dict=channel_dict,
                               channel_list=channel_list, index_dict=index_dict, side_bar_list=side_bar_list,
                               form=form, img_form=img_form)


@app.route("/class_dict", methods=['post'])
def get_class_dict():
    """返回小类数据"""
    data = json.dumps(channel.get_class_dict(1))
    return data


@app.route("/channel_<channel_id>.html")
def my_channel(channel_id):
    """列表页"""
    form = SearchLoginForm()  # 搜索from
    try:
        channel_id = int(channel_id)
    except ValueError:
        channel_id = 1
    login_flag = is_login(session)  # 用户是否已登录
    channel_list = channel.channel_list()  # 获取频道列表
    channel_name = ""  # 当前频道名称
    class_list = channel.get_class_dict()[channel_id]  # 获取频道所有小类
    current_class_id = int(get_arg(request, "class_id", 0))  # 获取当前小类ｉｄ

    for x in range(len(channel_list)):
        temp = channel_list[x]
        if temp['channel_id'] == channel_id:
            """获取频道名"""
            channel_name = temp['channel_name']
            break
    """获取频道的话题列表"""
    topic_list = topic.channel_topic_list(channel_id=channel_id, class_id=current_class_id)

    if login_flag:
        try:
            user_img_url = session['user_img_url']
        except KeyError:
            user_img_url = ""
        user_img_url = '../static/image/guest.png' if user_img_url == "" else session['user_img_url']
        user_level = 1  # 暂时替代

        return render_template("channel.html", login_flag=login_flag, channel_list=channel_list,
                               current_channel_name=channel_name, class_list=class_list,
                               current_channel_id=channel_id, current_class_id=current_class_id,
                               topic_list=topic_list, user_level=user_level, user_img_url=user_img_url,
                               form=form)

    else:
        return render_template("channel.html", login_flag=login_flag, channel_list=channel_list,
                               current_channel_name=channel_name, class_list=class_list,
                               current_channel_id=channel_id, current_class_id=current_class_id,
                               topic_list=topic_list, form=form)


@app.route("/detail_<key>.html")
def my_detail(key):
    """投票详细页"""

    form = RequestLoginForm()
    result = topic.topic_detail_user(top_id=key)
    if len(result['data']) == 0:
        abort(404)
    else:
        topic_info = result['data']
        surplus = surplus_datetime(topic_info['end_date'])  # 剩余时间
        all_view_count = vote_tools.get_view_count(topic_id=key)  # 浏览总数
        query_vote = vote_tools.get_vote_count(key)  # 查询　投票人数
        support_a = query_vote['support_a']
        support_b = query_vote['support_b']
        join_count = support_b + support_a  # 投票总人数
        side_bar_list = topic.side_bar_topic_list()  # 侧边栏的列表
        if support_a == 0 and join_count == 0:
            blue_width = 50
        else:
            blue_width = int((support_a / join_count) * 1000) / 10
        red_width = int(1000 - blue_width * 10) / 10

        login_flag = is_login(session)  # 用户是否已登录

        if login_flag:
            try:
                user_img_url = session['user_img_url']
            except KeyError:
                user_img_url = ""
            user_img_url = '../static/image/guest.png' if user_img_url == "" else session['user_img_url']
            user_level = 1  # 暂时替代

            return render_template("detail.html", topic_info=topic_info, surplus=surplus, join_count=join_count,
                                   blue_width=blue_width, red_width=red_width, all_view_count=all_view_count, form=form,
                                   login_flag=login_flag, user_img_url=user_img_url, user_level=user_level,
                                   side_bar_list=side_bar_list)

        else:
            return render_template("detail.html", topic_info=topic_info, surplus=surplus, join_count=join_count,
                                   blue_width=blue_width, red_width=red_width, all_view_count=all_view_count, form=form,
                                   login_flag=login_flag, side_bar_list=side_bar_list)


@app.route("/login", methods=['post', 'get'])
def my_login():
    """登录页面"""
    form = UserLoginForm()
    if request.method.lower() == 'get':
        """先确认是否由本站跳转来的，如果有，需要重定向"""
        host_url = request.host_url  # 取本站点的url
        base_url = request.base_url  # 取本视图页面url
        referrer = request.referrer
        url_path = request.path  # url路径
        print("host_url = {}".format(host_url))
        print("base_url = {}".format(base_url))
        print("referrer = {}".format(referrer))
        print("url_path = {}".format(url_path))
        redirect_url = None
        if referrer is None:  # 直接打开页面
            pass
        elif referrer == host_url or referrer == base_url:  # 刷新页面
            pass
        elif referrer.find(host_url) != -1 and request.args.get("ref") is None:  # 有本站的referrer的情况
            redirect_url = referrer.replace(host_url, "/")
            redirect_url = base64.b64encode(redirect_url.encode("utf8"))
            return redirect(url_for("my_login", ref=redirect_url))
        else:
            pass
        """真正的get视图函数开始"""
        show_img_code = 0  # 是否显示图形验证码
        login_flag = is_login(session)  # 用户是否已登录
        if login_flag:
            try:
                user_img_url = session['user_img_url']
            except KeyError:
                user_img_url = ""
            user_img_url = '../static/image/guest.png' if user_img_url == "" else session['user_img_url']
            user_level = 1  # 暂时替代
            return render_template("login.html", form=form, login_flag=login_flag,
                                   user_img_url=user_img_url, user_level=user_level,
                                   show_img_code=show_img_code)
        else:
            return render_template("login.html", form=form, login_flag=login_flag, show_img_code=show_img_code)
    else:
        """post视图函数，检查用户提交的身份信息"""
        message = {"message": "error"}
        if form.validate_on_submit():
            user_phone = request.form.get('phone')
            user_password = request.form.get('user_password')
            result = user_login_phone(user_phone, user_password)
            if result['message'] == 'success':
                user_id = result['data']['user_id']
                user_level = 1
                user_img_url = result['data']['user_img_url']
                set_user_login_info(session, user_id, user_password, user_img_url, user_level)
                message = result

            else:
                try:
                    session.pop("user_id")
                    session.pop("user_password")
                except KeyError:
                    pass
                finally:
                    message = result
        return json.dumps(message)


@app.route('/login_out')
def user_login_out():
    try:
        session.pop("user_id")
        session.pop("user_password")
        session.pop("user_img_url")
        session.pop("user_level")
    except KeyError:
        pass
    finally:
        return redirect(url_for("my_login"))


@app.route("/register", methods=['post', 'get'])
def my_register():
    form = UserRegForm()
    if request.method.lower() == 'get':
        """注册页面"""
        login_flag = is_login(session)  # 用户是否已登录
        if login_flag:
            try:
                user_img_url = session['user_img_url']
            except KeyError:
                user_img_url = ""
            user_img_url = '../static/image/guest.png' if user_img_url == "" else session['user_img_url']
            user_level = 1  # 暂时替代
            return render_template("register.html", form=form, login_flag=login_flag, user_img_url=user_img_url,
                                   user_level=user_level)
        else:
            return render_template("register.html", form=form, login_flag=login_flag)
    else:
        """检查注册"""
        message = {"message": "error"}
        if form.validate_on_submit():
            user_phone = request.form.get('phone')
            user_password = request.form.get('user_password')
            token = get_arg(request, "csrf_token")
            img_code = get_arg(request, "img_code")
            if token == "" or not check_img_code(token, img_code):
                message['message'] = '验证码错误'
            else:
                user_id = get_only_id()
                reg_args = {"user_phone": user_phone, "user_password": user_password,
                            "user_id": user_id, "create_date": current_datetime()}
                result = user.add_user(**reg_args)
                if result['message'] == 'success':
                    user_id = user_id
                    user_level = 1  # 临时替代
                    user_img_url = '../static/image/guest.png'
                    set_user_login_info(session, user_id, user_password, user_img_url, user_level)
                    message = result

                else:
                    message = result
            return json.dumps(message)


@app.route("/user_center_voter")
@login_required_user
def user_center_voter():
    """用户中心投票页面"""
    login_flag = is_login(session)  # 用户是否已登录
    if login_flag:
        """取用户名和密码"""
        try:
            user_id = session['user_id']
            user_password = session['user_password']
        except KeyError:
            abort(403)
        query_result = user.get_user_info(user_id, user_password)
        if query_result['message'] == "success":
            user_info = query_result['data']
            try:
                user_img_url = session['user_img_url']
            except KeyError:
                user_img_url = ""
            user_img_url = '../static/image/guest.png' if user_img_url == "" else session['user_img_url']
            user_level = 1  # 暂时替代
            created_topics = topic.fetch_created_topics(user_id)
            joined_topics = topic.fetch_joined_topics(user_id)
            starred_topics = topic.fetch_starred_topics(user_id)
            print(created_topics)
            return render_template("user_center_voter.html",
                                   login_flag=login_flag,
                                   user_img_url=user_img_url, user_level=user_level,
                                   user_info = user_info,
                                   created_topics = created_topics,
                                   joined_topics = joined_topics,
                                   starred_topics = starred_topics)
    else:
        return render_template("user_center_voter.html", login_flag=login_flag)


@app.route("/user_center_info")
@login_required_user
def user_center_info():
    """用户中心个人资料页面"""
    login_flag = is_login(session)  # 用户是否已登录
    zone_dict = zone_info()  # 获取一级行政区域信息
    children_list = zone_info(the_type="children")  # 获取默认的省市行政信息
    default_zone = {"zone_name": "上海市", "zone_id": zone_dict.get("上海市")}
    if login_flag:
        """取用户名和密码"""
        try:
            user_id = session['user_id']
            user_password = session['user_password']
        except KeyError:
            abort(403)
        query_result = user.get_user_info(user_id, user_password)
        if query_result['message'] == "success":
            user_info = query_result['data']
            try:
                user_img_url = session['user_img_url']
            except KeyError:
                user_img_url = ""
            user_img_url = '../static/image/guest.png' if user_img_url == "" else session['user_img_url']
            user_level = 1  # 暂时替代
            """如果有省/直辖市信息，那就重新获取二级行政划分的列表"""
            user_province = user_info['user_province']
            if user_province != "":
                children_list = zone_info(the_type="children", the_arg=zone_dict[user_province])
            """获取当前城市信息"""
            current_city = "选择 市/区"
            user_city = user_info['user_city']
            user_district = user_info['user_district']
            if user_city == "" and user_district == "":
                pass
            else:
                current_city = user_city if user_city != "" else user_district
            return render_template("user_center_info.html",
                                   default_zone=default_zone,
                                   children_list=children_list,
                                   zone_dict=zone_dict, login_flag=login_flag,
                                   user_img_url=user_img_url, user_level=user_level,
                                   user_info=user_info, current_city=current_city)
        else:
            return query_result['message']
    else:
        abort(404)


@app.route("/edit_user_info", methods=['post'])
@login_required_user
def edit_user_info():
    """用户编辑自己的信息"""
    the_form = request.form
    arg_dict = {key: the_form[key] for key in the_form.keys()}
    result = user.edit_user(**arg_dict)
    return json.dumps(result)


@app.route("/get_zone_info", methods=['post'])
def get_zone_info():
    """根据省市代码查询省市的行政信息"""
    message = {"message": "success"}
    the_id = request.form.get("the_id")
    if the_id is None:
        message['message'] = '参数缺失'
    else:
        result = zone_info("children", the_id)
        message["data"] = result
    return json.dumps(message)


@app.route("/image_code/<code>")
def image_code(code):
    """生成验证码"""
    code = code
    code = base64.b64decode(code).decode()
    the_image, the_code = creat_validata_code()
    img_io = io.BytesIO()
    the_image.save(img_io, "PNG")
    img_io.seek(0)
    cache.set(code, the_code, timeout=15 * 60)  # 写入缓存15分钟有效
    return send_file(img_io, mimetype='image/png', cache_timeout=0)  # cache_timeout=0是防止从缓存中读取


@app.route("/user_topic", methods=['post'])
@login_required_user
def user_topic():
    """用户对话题的操作"""
    form = SearchLoginForm()
    if form.validate_on_submit():
        the_form = request.form
        arg_dict = {key: the_form[key] for key in the_form.keys()}
        if arg_dict['the_type'] == "add":
            arg_dict['top_id'] = get_only_id()
            arg_dict['author'] = session['user_id']
            arg_dict['create_date'] = current_datetime()
        try:
            arg_dict.pop("csrf_token")
        except KeyError:
            pass
        result = topic.manage_topic(**arg_dict)
        return json.dumps(result)
    else:
        abort(403)


def allowed_file(filename):
    """检查上传文件类型"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/user_upload', methods=('GET', 'POST'))
@login_required_user
def user_upload():
    """用户上传图片"""
    astr = request.form.get("img_csrf")
    if check_img_csrf(astr):
        file = request.files['myfile']
        if file and allowed_file(file.filename):
            ab = request.form.get("file_select")
            filename = secure_filename(file.filename)  # 取文件类型
            filename = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f") + str(random.randint(10, 99)) + "." + \
                       filename  # 格式化到毫秒再加一个任意数
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            filepath = '../static/upload/images/' + filename
            return ab + "|" + filepath

        else:
            return "只允许图片类型的文件"
    else:
        return "未授权的访问"


@app.route('/user_portrait_upload', methods=('GET', 'POST'))
@login_required_user
def user_portrait_upload():
    """用户上传图片"""
    astr = request.form.get("img_csrf")
    if check_img_csrf(astr):
        file = request.files['myfile']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)  # 取文件类型
            filename = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f") + str(random.randint(10, 99)) + "." + \
                       filename  # 格式化到毫秒再加一个任意数
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            filepath = '../static/upload/images/' + filename
            user.edit_user(user_id= session['user_id'],user_img_url=filepath)
            session['user_img_url']=filepath
            return filepath
        else:
            return "只允许图片类型的文件"
    else:
        return "未授权的访问"


@app.route("/img_csrf", methods=['post'])
def img_csrf():
    """获取img_csrf"""
    return json.dumps(get_img_csrf())


@app.route('/admin_upload', methods=('GET', 'POST'))
@login_required_admin
def admin_upload():
    """管理员上传图片"""
    file = request.files['myfile']
    if file and allowed_file(file.filename):
        ab = request.form.get("file_select")
        filename = secure_filename(file.filename)  # 取文件类型
        filename = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f") + str(random.randint(10, 99)) + "." + \
                   filename  # 格式化到毫秒再加一个任意数
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        filepath = '../static/upload/images/' + filename
        return ab + "|" + filepath

    else:
        return "只允许图片类型的文件"


@app.route("/admin_login_page", methods=['post', 'get'])
def admin_login_page():
    """管理员登录页面"""
    form = AdminLoginForm()
    if request.method.lower() == "get":
        return render_template("admin_login.html", form=form)
    else:
        if form.validate_on_submit():
            """id: zvoter  pw: Zvoter666 """
            admin_name = get_arg(request, "admin_name")
            admin_password = get_arg(request, "admin_password")
            result = admin.login(admin_name, admin_password)
            if result['message'] == 'success':
                admin_id = result['data']['admin_id']
                set_admin_login_info(session, admin_id, admin_password)
                message = result

            else:
                try:
                    session.pop("admin_id")
                    session.pop("admin_password")
                except KeyError:
                    pass
                finally:
                    message = result
            return json.dumps(message)

        else:
            abort(400)


@app.route("/admin_center/<key>")
@login_required_admin
def admin_center(key):
    """后台管理页"""
    if key == "user":
        """用户管理"""
        user_count = user.user_count()
        current_index = int(get_arg(request, "index", 1))  # 取页码
        page_length = int(get_arg(request, "page_length", 20))  # 每页多少记录
        max_index = math.ceil(user_count / page_length)  # 最大页码
        if max_index < current_index:
            current_index = max_index
        if 1 > current_index:
            current_index = 1
        """每页显示5个可点击页码"""
        range_min = current_index - 2 if current_index > 2 else 1
        rang_max = max_index if (range_min + 4) > max_index else (range_min + 4)

        index_range = [x for x in range(range_min, rang_max + 1)]
        user_data = user.page(current_index, page_length)['data']
        return render_template("admin_center_user.html",
                               user_count=user_count,
                               index_range=index_range,
                               max_index=max_index,
                               current_index=current_index,
                               prev_index=current_index if (current_index - 1) > 1 else 1,
                               next_index=current_index + 1 if (current_index + 1) < max_index else max_index,
                               user_data=user_data)
    elif key == "channel":
        """频道管理"""
        channel_list = channel.channel_list(1)
        small_class_dict = channel.get_class_dict(1)

        return render_template("admin_center_channel.html", channel_list=channel_list,
                               small_class_dict=small_class_dict)

    elif key == "topic":
        """话题管理"""
        form = SearchLoginForm()
        topic_count = topic.topic_count()
        current_index = int(get_arg(request, "index", 1))  # 取页码
        page_length = int(get_arg(request, "page_length", 5))  # 每页多少记录
        max_index = math.ceil(topic_count / page_length)  # 最大页码
        if max_index < current_index:
            current_index = max_index
        if 1 > current_index:
            current_index = 1
        """每页显示5个可点击页码"""
        range_min = current_index - 2 if current_index > 2 else 1
        rang_max = max_index if (range_min + 4) > max_index else (range_min + 4)

        index_range = [x for x in range(range_min, rang_max + 1)]
        topic_data = topic.manage_topic_admin(the_type="page", index=current_index, page_length=page_length)
        topic_data = topic_data['data']
        channel_list = channel.channel_list()
        return render_template("admin_center_topic.html",
                               channel_list=channel_list,
                               topic_count=topic_count,
                               index_range=index_range,
                               max_index=max_index,
                               current_index=current_index,
                               prev_index=current_index if (current_index - 1) > 1 else 1,
                               next_index=current_index + 1 if (current_index + 1) < max_index else max_index,
                               topic_data=topic_data, form=form)


@app.route("/manage_<key1>/<key2>", methods=['post'])
@login_required_admin
def manage_handler(key1, key2):
    """对后台的编辑接口"""
    message = {"message": "未知操作类型"}
    if key1 == "user":
        """管理用户"""

        """取参数集"""
        the_form = request.form
        arg_dict = {key: the_form[key] for key in the_form.keys()}
        if key2 == "up_user":
            message = up_user(arg_dict['user_id'])
        elif key2 == "down_user":
            message = down_user(arg_dict['user_id'])
        elif key2 == "drop_user":
            message = drop_user(arg_dict['user_id'])
        else:
            pass

    elif key1 == "class":
        """对类别的操作"""
        if key2 == "save":
            the_form = request.form
            arg_dict = {key: json.loads(the_form[key]) for key in the_form.keys()}
            result = channel.save_class(arg_dict)
            if result:
                message = result
            else:
                message = {"message": "保存类别信息失败"}

    elif key1 == "topic":
        """对话题的操作"""
        if key2 == "edit":
            """编辑话题"""
            the_form = request.form
            arg_dict = dict()
            for key in the_form.keys():
                temp = the_form[key]
                if temp is not None:
                    arg_dict[key] = temp
            result = topic.manage_topic_admin(**arg_dict)
            return json.dumps(result)
        elif key2 == "up_topic":
            """审核帖子"""
            the_form = request.form
            arg_dict = dict()
            for key in the_form.keys():
                temp = the_form[key]
                if temp is not None:
                    arg_dict[key] = temp
            result = topic.manage_topic_admin(**arg_dict)
            return json.dumps(result)

        elif key2 == "down_topic":
            """停用帖子"""
            the_form = request.form
            arg_dict = dict()
            for key in the_form.keys():
                temp = the_form[key]
                if temp is not None:
                    arg_dict[key] = temp
            result = topic.manage_topic_admin(**arg_dict)
            return json.dumps(result)

        elif key2 == "drop_topic":
            """删除帖子"""
            the_form = request.form
            arg_dict = dict()
            for key in the_form.keys():
                temp = the_form[key]
                if temp is not None:
                    arg_dict[key] = temp
            result = topic.manage_topic_admin(**arg_dict)
            return json.dumps(result)


    else:
        abort(403)
    return json.dumps(message)


@app.route("/view/<key>.html")
@login_required_admin
def view_topic(key):
    """管理员浏览话题的详细页"""
    form = RequestLoginForm()
    result = topic.manage_topic_admin(top_id=key, the_type="single")
    topic_info = result['data']
    surplus = surplus_datetime(topic_info['end_date'])  # 剩余时间
    all_view_count = vote_tools.get_view_count(topic_id=key)  # 浏览总数
    query_vote = vote_tools.get_vote_count(key)  # 查询　投票人数
    support_a = query_vote['support_a']
    support_b = query_vote['support_b']
    join_count = support_b + support_a  # 投票总人数
    if support_a == 0 and join_count == 0:
        blue_width = 50
    else:
        blue_width = int((support_a / join_count) * 1000) / 10
    red_width = 100 - blue_width
    return render_template("detail.html", topic_info=topic_info, surplus=surplus, join_count=join_count,
                           blue_width=blue_width, red_width=red_width, all_view_count=all_view_count, form=form)


@app.route("/vote", methods=['post', 'get'])
def vote():
    """用户投票计数"""
    form = RequestLoginForm()
    message = {'message': 'success'}
    if form.validate_on_submit():
        only_id = get_arg(request, 'canvas_uuid')
        topic_id = get_arg(request, 'topic_id')
        try:
            user_id = session['user_id']
        except KeyError:
            user_id = ''
        from_ip = get_real_ip(request)
        browser_type = get_user_agent(request)
        viewpoint = get_arg(request, "viewpoint")
        support_a = 1 if viewpoint == "a" else 0
        support_b = 1 if viewpoint == "b" else 0
        args = {'only_id': only_id, 'user_id': user_id, 'topic_id': topic_id,
                'from_ip': from_ip, 'browser_type': browser_type,
                'support_a': support_a, 'support_b': support_b}
        result = vote_tools.vote(**args)
        message = result

    else:
        message['message'] = '未登录'  # 并非投票要求登录，这个提示是给刷投票的机器准备的

    return json.dumps(message)


@app.route("/view_count")
def view_count():
    """页面浏览计数"""
    only_id = get_arg(request, "canvas_uuid")
    topic_id = get_arg(request, "topic_id")
    from_ip = get_real_ip(request)
    browser_type = get_user_agent(request)
    result = vote_tools.add_view_count(topic_id=topic_id, only_id=only_id, from_ip=from_ip, browser_type=browser_type)
    return json.dumps(result)


@app.route("/user_comment", methods=['post'])
@login_required_user
def user_comment():
    """用户留言"""
    pass

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True, threaded=True)
