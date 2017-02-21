/**
 * Created by walle on 17-2-8.
 */
$(function(){
    // 启用账户
    up_user = function ($obj){
        var user_id = $obj.attr("data-id");
        $.post("/manage_user/up_user", {"user_id": user_id}, function(data){
            var data = JSON.parse(data);
            if(data['message'] == 'success'){
                alert("启用成功");
                location.reload();
            }
            else{
                alert(data['message']);
            }
        });
    };

    // 禁用账户
    down_user = function ($obj){
        var user_id = $obj.attr("data-id");
        $.post("/manage_user/down_user", {"user_id": user_id}, function(data){
            var data = JSON.parse(data);
            if(data['message'] == 'success'){
                alert("禁用成功");
                location.reload();
            }
            else{
                alert(data['message']);
            }
        });
    };

    // 删除账户
    drop_user = function ($obj){
        var user_id = $obj.attr("data-id");
        $.post("/manage_user/drop_user", {"user_id": user_id}, function(data){
            var data = JSON.parse(data);
            if(data['message'] == 'success'){
                alert("删除成功");
                location.reload();
            }
            else{
                alert(data['message']);
            }
        });
    };





    //end !
});