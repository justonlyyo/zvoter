/**
 * Created by walle on 17-2-20.
 */
$(function(){

    var csrf_token = $("#csrf_token").val();
    var topic_id = $("#current_topic_id").text();
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

    //end！
});