/**
 * Created by walle on 2017/2/4.
 */
$(function(){
    // 验证码图像
    function get_img() {
        var par = $("#img_code").parent();
        $("#img_code").attr("src", '/image_code/' + $.base64.btoa($("#csrf_token").val(), true) + "?uid=" + Math.random()).css({
            "width": par.width(), "height": $("#sms_code").height() + 14
        });

    }

    get_img();

    // 点击获取新的验证码
    $("#img_code").click(function () {
        get_img()
    });
    function resize_img() {
        $("#img_code").css({
            "width": $("#img_code").parent().width(), "height": $("#sms_code").height() + 14
        });
    }

    // 调整验证码尺寸
    $(window).resize(function () {
        resize_img();
    });

    // 提交前检查表单
    function check_form() {
        if (!validate_phone($.trim($("#phone").val()))) {
            alert("手机号码错误");
            return false;
        }
        else if ($.trim($("#password").val()) == 0 || $.trim($("#password").val()).length < 6) {
            alert("密码至少6位");
            return false;
        }
        else if($.trim($("#password").val()) != $.trim($("#re_password").val())){
            alert("两次输入的密码不一致");
            return false;
        }
        else if ($.trim($("#sms_code").val()).length != 4 && show_img_code == 1) {
            alert("验证码错误");
            return false;
        }
        else {
            var password = $.trim($("#password").val());
            console.log(password);
            $("#password").val($.md5(password));
            $("#re_password").val($.md5(password));
            return true;
        }
    }

    // 绑定按钮
    bind_enter_event($("#phone"), $("#password"));
    bind_enter_event($("#password"), $("#re_password"));
    bind_enter_event($("#re_password"), $("#sms_code"));
    bind_enter_event($("#sms_code"), $("#submit_btn"));

    // 打开页面时清除表单的值
    $("#phone,#password,#re_password,#sms_code").val("");

    // 提交事件
    $("#submit_btn").click(function () {
        if (check_form()) {
            var user_nickname = $.trim($("#nickname").val());
            var phone = $.trim($("#phone").val());
            var user_password = $.trim($("#password").val());
            var img_code = $.trim($("#sms_code").val());  // 图形验证码
            var csrf_token = $("#csrf_token").val();
            // var referrer = document.referrer;
            var args = {
                "phone": phone, "user_password": user_password,
                "img_code": img_code, "csrf_token": csrf_token,
                "user_nickname": user_nickname
            };
            $("#submit_btn").prop("disabled","disabled");
            $.post("/register", args, function (data) {
                 $("#submit_btn").removeAttr("disabled");
                var data = JSON.parse(data);
                if (data['message'] != 'success') {
                    alert(data['message']);
                    $("#password,#re_password").val("");
                    return false;
                }
                else {
                    location.href = before_url;
                }
            });
        }
        else{
            //nothing...
            console.log(1);
        }
    });

    //end!
});
