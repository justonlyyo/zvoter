$(function () {
    // 编辑话题事件
    edit_topic = function ($obj) {
        tr_to_modal($obj);
        $("#pop_modal").click();

    };

    // 把tr内的数据加载到模态框
    tr_to_modal = function ($obj) {
        var $tr = $obj.parents(".my_topic:first");
        var top_id = $tr.attr("id").split("id_")[1];
        var top_title = $tr.find(".top_title").text();
        var top_content = $tr.find(".top_content").text();
        var channel_id = $tr.find(".channel_id").text();
        var class_id = $tr.find(".class_id").text();
        var viewpoint_a = $tr.find(".viewpoint_a").text();
        var img_url_a = $tr.find(".img_url_a").text();
        var viewpoint_b = $tr.find(".viewpoint_b").text();
        var img_url_b = $tr.find(".img_url_b").text();
        var can_show = $tr.find(".can_show").attr("data-val");
        var begin_date = $tr.find(".begin_date").text();
        var end_date = $tr.find(".end_date").text();
        var author = $tr.find(".author").text();

        // 赋值
        $("#top_id").val(top_id);
        $("#top_title").val(top_title);
        $("#top_content").val(top_content);
        $("#big_class").val(channel_id);
        var class_list = global_class_dict[$("#big_class").val()];
        var select = $("#small_class");
        select.empty();
        for (var i = 0, l = class_list.length; i < l; i++) {
            var temp = class_list[i];
            select.append('<option value="' + temp['class_id'] + '">' + temp['class_name'] + '</option>');
        }
        $("#small_class").val(class_id);
        $("#select_a").val(viewpoint_a);
        $("#select_b").val(viewpoint_b);
        $("#begin_date").val(begin_date);
        $("#end_date").val(end_date);
        $("#select_b").val(viewpoint_b);
        $("#img_url_a").val(img_url_a);
        $("#img_url_b").val(img_url_b);
        if (img_url_a != "") {
            $(".add_img[data-ab='a']").text("编辑图片");
            $(".add_img[data-ab='b']").text("编辑图片");
        }
    };

    // 加载小类
    $.post("/class_dict", function (data) {
        global_class_dict = JSON.parse(data);  // 全局变量
        $("#big_class").change(function () {
            var class_list = global_class_dict[$("#big_class").val()];
            var select = $("#small_class");
            select.empty();
            for (var i = 0, l = class_list.length; i < l; i++) {
                var temp = class_list[i];
                select.append('<option value="' + temp['class_id'] + '">' + temp['class_name'] + '</option>');
            }
        });

    });

    // 文件改动的监听事件
    var $current_add_img = null;
    $("#my_file").change(function () {
        // 请求img_csrf
        $.post("/img_csrf", function (data) {
            var data = JSON.parse(data);
            var the_val = data['id'] + "|" + data['val'];
            $("#img_csrf").val(the_val);
            var ab = $current_add_img.attr("data-ab");
            $("#file_select").val(ab);
//                    show_tips(1);  // 显示上传提示框
            // 确认接收容器
            $("#file_form").attr("target", "exec_target_" + ab);
            $("#submit_img_button").click();  // 提交文件
            var file_name = $("#my_file").val();
            $current_add_img.attr("data-url", file_name);

        });

    });


    // 图片上传
    $(".add_img").click(function () {
        $current_add_img = $(this);
        $("#my_file").val("").click();
    });

    // 上传图片成功后
    $("#exec_target_a").load(function () {
        var data = $(window.frames['exec_target_a'].document.body).html();  //上传文件返回
        console.log(data);
        if ($.trim(data) != "") {
            var temp = data.split("|");
            if (temp.length == 2) {
                var ab = temp[0];
                var src = temp[1];
                $("#img_url_a").val(src);
                $(".add_img[data-ab='a']").text("添加完成");
            }
            else {
                alert(data);
            }
        }
    });
    $("#exec_target_b").load(function () {
        var data = $(window.frames['exec_target_b'].document.body).html();  //上传文件返回
        if ($.trim(data) != "") {
            var temp = data.split("|");
            if (temp.length == 2) {
                var ab = temp[0];
                var src = temp[1];
                $("#img_url_b").val(src);
                $(".add_img[data-ab='b']").text("添加完成");
            }
            else {
                alert(data);
            }
        }
    });

    // 审核帖子
    up_topic = function($obj){
        var top_id = $obj.parents(".my_topic:first").attr("id").split("id_")[1];
        $.post("/manage_topic/up_topic", {"top_id": top_id, "the_type": "up"},function(data){
            var data = JSON.parse(data);
            if(data['message'] == "success"){
                alert("审核成功");
                location.href = location.href;
            }
            else{
                alert(data['message']);
            }
        });
    };

    // 停用帖子
    down_topic = function($obj){
        var top_id = $obj.parents(".my_topic:first").attr("id").split("id_")[1];
        $.post("/manage_topic/down_topic", {"top_id": top_id, "the_type": "down"},function(data){
            var data = JSON.parse(data);
            if(data['message'] == "success"){
                alert("停用成功");
                location.href = location.href;
            }
            else{
                alert(data['message']);
            }
        });
    };

    // 删除帖子
    drop_topic = function($obj){
        var top_name = $obj.parents(".my_topic:first").find(".top_title").text();
        var con = confirm("你确实想删除《"+top_name+"》这个帖子吗？");
        if(con){
            var top_id = $obj.parents(".my_topic:first").attr("id").split("id_")[1];
            $.post("/manage_topic/drop_topic", {"top_id": top_id, "the_type": "drop"},function(data){
                var data = JSON.parse(data);
                if(data['message'] == "success"){
                    alert("删除成功");
                    location.href = location.href;
                }
                else{
                    alert(data['message']);
                }
            });
        }
    };


    $("#begin_date,#end_date").attr("readonly", "true");
    // 提交事件
    var submit_topic = function () {
        var top_id = $.trim($("#top_id").val());
        var top_title = $.trim($("#top_title").val());
        var top_content = $.trim($("#top_content").val());
        var channel_id = $("#big_class").val();
        var class_id = $("#small_class").val();
        var select_a = $.trim($("#select_a").val());
        var select_b = $.trim($("#select_b").val());
        var img_url_a = $.trim($("#img_url_a").val());
        var img_url_b = $.trim($("#img_url_b").val());
        var begin_date = "";
        var end_date = "";
        if ($("#set_forever:checked").length != 1) {
            begin_date = $("#begin_date").val();
            end_date = $("#end_date").val();
        }

        if (top_title == "") {
            alert("标题不能为空");
            return false;
        }
        else if (top_content == "") {
            alert("话题描述不能为空");
            return false;
        }
        else if (select_a == "") {
            alert("选项1不能为空");
            return false;
        }
        else if (select_b == "") {
            alert("选项2不能为空");
            return false;
        }
        else if (channel_id == "") {
            alert("频道大类不能为空");
            return false;
        }
        else if (class_id == "") {
            alert("频道小类不能为空");
            return false;
        }
        else {
            var args = {
                "top_title": top_title, "top_content": top_content,
                "viewpoint_a": select_a, "viewpoint_b": select_b, "img_url_a": img_url_a,
                "img_url_b": img_url_b, "begin_date": begin_date, "end_date": end_date,
                "channel_id": channel_id, "class_id": class_id, "top_id": top_id,
                "the_type": "edit"
            };
            $.post("/manage_topic/edit", args, function (data) {
                var data = JSON.parse(data);
                if (data['message'] == 'success') {
                    alert("提交成功");
                    $("#myModal input").val("");
                    $("#myModal textarea").val("");
                    location.href = location.href;
                }
                else {
                    alert(data['message']);
                }
            });
        }
    };
    $("#vote_submit_btn").click(function () {
        submit_topic();
    });


    // end!
});
