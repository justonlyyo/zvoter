/**
 * Created by walle on 17-2-7.
 */
$(function(){
    // 提交事件
    $("#submit_btn").click(function(){
        var admin_name = $.trim($("#admin_name").val());
        var admin_password = $.trim($("#admin_password").val());
        var csrf_token = $.trim($("#csrf_token").val());
        if(admin_name == ""){
            alert("用户名不能为空");
            return false;
        }
        else if(admin_password == ""){
            alert("密码不能为空");
            return false;
        }
        else if(csrf_token == ""){
            alert("提交错误");
            return false;
        }
        else{
            var args = {"admin_name": admin_name,
            "admin_password": $.md5(admin_password),
            "csrf_token": csrf_token};
            $.post("/admin_login_page", args, function(data){
                var data = JSON.parse(data);
                console.log(data);
                if(data['message'] == 'success'){
                    location.href = "/admin_center/user";
                }
                else{
                    alert(data['message']);
                }
            });
        }
    });

    // 绑定回车键
    bind_enter_event($("#admin_name"), $("#admin_password"));
    bind_enter_event($("#admin_password"), $("#submit_btn"));

// end!
});