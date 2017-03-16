/**
 * Created by walle on 17-2-20.
 */
$(function(){

    var csrf_token = $("#csrf_token").val();
    var topic_id = $("#current_topic_id").text();
    var is_voted = "";
    var login_flag = $.trim($("#login_flag").text()) == "1";  // 是否已登录

    // 加载页面时检查是否已经投过票了。
    $.get("/is_voted", {"canvas_uuid": canvas_uuid, "topic_id": topic_id}, function(data){
        var data = JSON.parse(data);
        if(data == ""){
            $("#my_message").val('').attr("readonly", "readonly").attr("placeholder", "先投票再吐槽");
        }
        else if(!login_flag && data != ""){
            $("#my_message").val('').attr("readonly", "readonly").attr("placeholder", "先登录再吐槽");
            is_voted = data;
        }
        else{
            $("#my_message").val('').attr("placeholder", "欢迎吐槽");
            is_voted = data;
        }
    });

    // 投票按钮
    $(".voter_btn").click(function(){
        var $this =  $(this);
        var the_class = $this.attr("class");
        console.log(the_class);
        if(the_class.indexOf("btn_a") != -1){
            vote("a");
        }
        else{
            vote("b");
        }
    });

    // 投票事件
    vote = function(val){
        $.post("/vote", {"viewpoint": val,
            "canvas_uuid": canvas_uuid,
        "csrf_token": csrf_token,
        "topic_id": topic_id}, function(data){
            var data = JSON.parse(data);
            if(data['message'] == 'success'){
                alert("投票成功！");
                location.href = location.href;
            }
            else{
                alert(data['message']);
            }
        });
    };

    // 用户留言
    $("#submit_btn").click(function(){
        var comment_text = $.trim($("#my_message").val());
        if(comment_text == ""){
            //nothing...
        }
        else{
            var parent_comment = $.trim($("#comment_obj").attr("data_parent_comment"));
            var support_side = is_voted;
            var args = {'topic_id': topic_id,
            "parent_comment": parent_comment, "csrf_token": csrf_token,
            "support_side": support_side, "comment_text": comment_text
            };
            $.post("/user_comment/add", args, function(data){
                var data = JSON.parse(data);
                if(data['message'] == 'success'){
                    alert("提交成功");
                    $("#my_message").val('');
                    location.href = location.href.split("#")[0];
                }
                else{
                    alert(data['message']);
                }
            });

        }
    });

    //end！
});