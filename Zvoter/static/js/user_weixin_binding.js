/**
 * Created by zhouyi on 17-3-15.
 */
$(function () {
    $(".old_user").click(function () {
        // $(".binding-weixin-form").toggle();
        window.location = "http://www.zvoter.com/login"
    });
    $(".new_user").click(function () {
        $.post("/weixin_new_user", function (data) {
            // alert(data.message)
            var data = JSON.parse(data);
            if (data.message == 'success'){
                // alert("success")
                window.location = "http://www.zvoter.com/"
            }else {
                console.log(data);
                alert("服务器开小差了..");
                alert(data.result)
            }
        });
    });
});