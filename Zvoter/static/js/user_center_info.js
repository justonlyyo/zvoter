/**
 * Created by walle on 2017/1/31.
 */
$(function () {
    // 头像上传
    $(".change_portrait").click(function () {
        var $this = $(this);
        $("#my_file").val("").click().change(function () {
            // 请求img_csrf
            $.post("/img_csrf", function (data) {
                var data = JSON.parse(data);
                var the_val = data['id'] + "|" + data['val'];
                $("#img_csrf").val(the_val);
                $("#submit_img_button").click();  // 提交文件
                var file_name = $("#my_file").val();
                $this.attr("data-url", file_name);
            });

        });
    });

    // 头像上传成功后
    $("#upload_portrait_target").load(function () {
        var data = $(window.frames['upload_portrait_target'].document.body).html();  //上传文件返回
        console.log(data);
        if ($.trim(data) != "") {
            $("#user_img").attr("src", data);
            $("#login_user_pic").attr("src", data);
        }
    });

    // 选择城市的回调函数
    function select_zone(data) {
        var data = JSON.parse(data);
        if (data['message'] == 'success') {
            data = data['data'];
            var first = data[0];
            $("#children_btn").attr('data-id', first).html(first + "<span class='caret'></span>");
            var ul = $("#children_ul");
            ul.empty();
            for (var i = 0, l = data.length; i < l; i++) {
                var val = data[i];
                ul.append("<li data-id=" + val + ">" + val + "</li>");
            }
            ul.find("li").click(function () {
                var $this = $(this);
                var id = $this.attr("data-id");
                var name = $this.text();
                var obj = $this.parent().parent().find("button:first");
                obj.attr("data-id", id).html(name + "<span class='caret'></span>");
            });
        }
    }

    // 选择省市按钮
    $(".select_zone>li").click(function () {
        var $this = $(this);
        var id = $this.attr("data-id");
        var name = $this.text();
        var obj = $this.parent().parent().find("button:first");
        obj.attr("data-id", id).html(name + "<span class='caret'></span>");
        if ($this.attr("class").indexOf("my_city") != -1) {
            $.post("/get_zone_info", {"the_id": id}, function (data) {
                select_zone(data);
            });
        }
    });

    // 选择星座
    $("#sign_select_ul>li").click(function () {
        $("#user_sign").val($(this).text());
    });

    // 载入页面时初始化一些模板不方便传递的值
    function init_val(){
        var user_sex = user_info['user_sex'];
        $("#user_sex input[data-val='"+user_sex+"']").click();
    }
    init_val();

    // 提交前检查
    $("#save_btn").click(function(){
        var user_id = user_info['user_id'];
        var user_nickname = $.trim($("#user_nickname").val());
        var user_sex = typeof($("#user_sex input:checked").attr("data-val")) == "undefined" ? "" : $.trim($("#user_sex input:checked").attr("data-val"));
        var user_sign = $.trim($("#user_sign").val());
        var user_mail = $.trim($("#user_mail").val());
        // 取省/直辖市
        var user_province = $("#user_province").attr("data-id") != "0" ? $("#user_province").text() : "";
        user_province = $.trim(user_province);
        // 取地级市/区
        var user_city = $("#children_btn").text() != "选择 市/区" ? $("#children_btn").text() : "";
        user_city = $.trim(user_city);
        var user_district = "";
        if(["北京市","天津市","上海市","重庆市"].indexOf(user_province) != -1){
            user_district = user_city;
            user_city = "";
        }
        var user_address = $.trim($("#user_address").val());
        var user_password = $.trim($("#user_password").val());
        var re_password = $.trim($("#re_password").val());
        var user_realname = $.trim($("#user_realname").val());
        var user_id_card = $.trim($("#user_id_card").val());
        var user_born_date = $.trim($("#user_born_date").val());
        var user_post_code = $.trim($("#user_post_code").val());

        if(!validate_mail(user_mail) && user_mail != ""){
            alert("邮箱地址错误");
            return false;
        }
        else if(user_password != re_password){
            alert("两次输入的密码不一致");
            return false;
        }
        else{
            var arg_dict = {"user_id": user_id, "user_nickname": user_nickname, "user_sex": user_sex,
            "user_sign": user_sign, "user_mail":user_mail, "user_province": user_province,
                "user_city": user_city, "user_district": user_district, "user_address": user_address,
            "user_realname": user_realname, "user_id_card": user_id_card,
            "user_post_code": user_post_code};
            if(user_password != ""){
                arg_dict["user_password"] = $.md5(user_password);
            }

            if(validate_date(user_born_date)){
                arg_dict['user_born_date'] = user_born_date;
            }

            $.post("/edit_user_info", arg_dict , function(data){
                var data = JSON.parse(data);
                if(data['message'] == 'success'){
                    if(typeof(arg_dict['user_password']) != "undefined"){
                        alert("密码修改成功，请注销后重新登录");
                        location.href = "/login_out";
                    }
                    else{
                        alert("资料修改成功");
                        location.reload();
                    }
                }
                else{
                    alert(data['message']);
                }
            });
        }

    });

    //end!
});
