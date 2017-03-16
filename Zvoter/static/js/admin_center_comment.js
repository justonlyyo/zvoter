$(function () {
    // 启动时渲染状态颜色
    $(".current_status").each(function(){
        var $this = $(this);
        var current_status = $.trim($this.attr("data_status"));
        $this.css("color", get_color(current_status));
    });

    // 审核事件
    function change_status($obj){
        var comment_status = $.trim($obj.attr("data_status"));
        var comment_text = $.trim($obj.text());
        var current_obj = $obj.parents("tr:first").find(".current_status");
        var comment_id = $obj.parents("tr:first").attr("id").split("_")[1];
        var args = {
            "comment_status": comment_status,
            "comment_id": comment_id
        };
        $.post("/manage_comment/edit", args, function(data){
            var data = JSON.parse(data);
            if(data['message'] == 'success'){
                current_obj.html(comment_text + "<span class='caret'></span>");
                current_obj.css("color", get_color(comment_status));
            }
            else{
                alert(data['message']);
            }
        });
    }

    // 审核动作
    $("#select_status a").click(function(){
        var $this = $(this);
        var selected_text = $.trim($this.text());
        var current_obj = $this.parents("tr:first").find(".current_status");
        if(selected_text != $.trim(current_obj.text())){
            // 提交审核事件
            change_status($this);
        }
        else{
            // nothing...
        }
    });

    // 删除评论
    drop_comment = function($obj){
        var comment_id = $.trim($obj.parents("tr:first").attr("id").split("_")[1]);
        var r = confirm("你确实要删除这条评论吗?");
        if(r){
            $.post("/manage_comment/delete", {"comment_id": comment_id}, function(data){
                var data = JSON.parse(data);
                if(data['message'] == 'success'){
                    alert("删除成功");
                    location.href = location.href;
                }
                else{
                    alert(data['message']);
                }
            });
        }else{}
    };


    // end!
});
