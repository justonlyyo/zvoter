/**
 * Created by walle on 2017/2/1.
 */
$(function () {
    // 验证手机号码的函数,不合法的手机号码会返回false
    validate_phone = function (phone) {
        var myreg = /^(((1[3-9][0-9]{1})|(15[0-9]{1})|(18[0-9]{1}))+\d{8})$/;
        if (myreg.test(phone)) {
            return true;
        }
        else {
            return false;
        }
    };

    // 检查邮箱
    validate_mail = function (str) {
        var reg = /^([a-zA-Z0-9_-])+@([a-zA-Z0-9_-])+((\.[a-zA-Z0-9_-]{2,3}){1,2})$/;
        return reg.test(str);
    };

    // 检查日期是否是 1900-12-12 这种格式
    validate_date = function (str) {
        var pattern = /^[12][09][0-9][0-9]-[01][0-9]-[0-3][0-9]$/;
        return pattern.test(str);
    };

    //一个用于绑定input输入框的回车事件的函数，需要实现的功能如下：
    //当本元素处于焦点状态时，如果发生了回车事件，光标会跳到下一个。如果下一个元素是提交按钮，那就触发提交动作。
    //2个参数 $obj1,被绑定的元素的jq对象  ，$obj2 下一个元素的jq对象 .
    bind_enter_event = function ($obj1, $obj2) {
        var $obj1 = $obj1;
        var $obj2 = $obj2;
        $obj1.keydown(function (e) {
            if (e.keyCode == 13) {
                $obj2.trigger("focus");
            } else {
            }
        });
    };

    before_url = "/";  // 全局变量，存放登录前的页面。
    // 取登录前的页面url的方法
    get_before_url = function () {
        var temp = location.href.split("?ref=");
        if (temp.length == 2) {
            /*服务端对这段字符串进行了url编码，这里必须解码*/
            var part = $.trim(temp[1].replace(location.host, ''));
            var b_str = decodeURIComponent(part);
            /*jquery base64 插件的解密方法，对应的加密方法叫$.base64.btoa，
             第二个参数的意思是支持不支持utf8，如果没有这个参数或者设置为false的话，
             就无法对中文进行加密解密*/
            before_url = $.base64.atob(b_str, true);
        }
    };
    get_before_url();


    //end!
});
