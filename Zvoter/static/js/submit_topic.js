$(function () {

    // 检查用户是否可以发起投票
    $(".pop_modal").mousedown(function(){
        var flag = $("#login_flag").text();
        if(flag != "1"){
            alert("请先登录");
            location.href = "/login";
            return false;
        }
        else{
            $("#pop_modal").click();
        }
    });

    // 加载小类
    $.post("/class_dict", function (data) {
        var class_dict = JSON.parse(data);
        $("#big_class").change(function () {
            var class_list = class_dict[$("#big_class").val()];
            var select = $("#small_class");
            select.empty();
            for (var i = 0, l = class_list.length; i < l; i++) {
                var temp = class_list[i];
                select.append('<option value="' + temp['class_id'] + '">' + temp['class_name'] + '</option>');
            }
        });

    });

    // 默认选择永久
    $("#set_forever").click();

    // 文件改动的监听事件
    var $current_add_img = null;
    $("#my_file").change(function () {
        // 检测信息
        var file_size = $(this)[0].files[0].size;
        console.log(file_size);
        if(file_size > 300*1024){
            alert("图片尺寸不可大于800K");
            return false;
        }
        else{
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
                $("#submit_img_button").click();  // 提交上传的文件
                var file_name = $("#my_file").val();
                $current_add_img.attr("data-url", file_name);

            });
        }
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
        if($.trim(data) != ""){
            var temp = data.split("|");
            if(temp.length == 2){
                var ab = temp[0];
                var src = temp[1];
                $("#img_a_url").val(src);
                $(".add_img[data-ab='a']").text("添加完成");
            }
            else{
                alert(data);
            }
        }
    });
    $("#exec_target_b").load(function () {
        var data = $(window.frames['exec_target_b'].document.body).html();  //上传文件返回
        if($.trim(data) != ""){
            var temp = data.split("|");
            if(temp.length == 2){
                var ab = temp[0];
                var src = temp[1];
                $("#img_b_url").val(src);
                $(".add_img[data-ab='b']").text("添加完成");
            }
            else{
                alert(data);
            }
        }
    });

    $("#begin_date,#end_date").attr("readonly", "true");
    // 提交事件
    var submit_topic = function () {
        var topic_title = $.trim($("#topic_title").val());
        var topic_content = $.trim($("#topic_content").val());
        var channel_id = $("#big_class").val();
        var class_id = $("#small_class").val();
        var select_a = $.trim($("#select_a").val());
        var select_b = $.trim($("#select_b").val());
        var img_url_a = $.trim($("#img_a_url").val());
        var img_url_b = $.trim($("#img_b_url").val());
        var begin_date = "";
        var end_date = "";
        if ("#set_forever:selected" != 1) {
            begin_date = $("#begin_date").val();
            end_date = $("#end_date").val();
        }

        if (topic_title == "") {
            alert("标题不能为空");
            return false;
        }
        /*
        else if (topic_content == "") {
            alert("话题描述不能为空");
            return false;
        }*/
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
            var csrf_token = $("#csrf_token").val();
            var args = {
                "top_title": topic_title, "top_content": topic_content,
                "viewpoint_a": select_a, "viewpoint_b": select_b, "img_url_a": img_url_a,
                "img_url_b": img_url_b, "begin_date": begin_date, "end_date": end_date,
                "channel_id": channel_id, "class_id": class_id,
                "csrf_token": csrf_token, "the_type": "add"
            };
            $.post("/user_topic", args, function(data){
                var data = JSON.parse(data);
                if(data['message'] == 'success'){
                    alert("提交成功");
                    $("#myModal input").val("");
                    $("#myModal textarea").val("");
                    location.href = location.href;
                }
                else{
                    alert(data['message']);
                }
            });
        }
    };
    $("#vote_submit_btn").click(function(){submit_topic();});


    // end!
});
