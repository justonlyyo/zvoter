/**
 * Created by walle on 17-3-9.
 */
$(function(){
    // 启动时清空表单
    function clear_input(){
        $("#banner_url,#banner_alt").val('');
    }
    clear_input();

    // 添加banner按钮
    $("#add_banner_btn").click(function(){
        $("#pop_modal").click();
        $("#myModalLabel").text('添加banner');
    });

    //修改排序函数
    function edit_index($this){
        var $obj = $this;
        var the_index = $.trim($obj.val());
        if(isNaN(the_index)){
            //nothing....
        }
        else{
            if(the_index == $obj.attr("data-before")){
                //nothing...
            }
            else{
                var banner_id = $.trim($obj.parents("tr:first").find(".banner_id").text());
                var banner_alt = $.trim($obj.parents("tr:first").find(".banner_alt").text());
                var banner_url = $.trim($obj.parents("tr:first").find(".banner_url").text());
                var args = {"banner_id": banner_id, "order_index": the_index, "banner_url": banner_url,
                    "banner_alt": banner_alt};
                $.post("/manage_banner/edit", args, function(data){
                    var data = JSON.parse(data);
                    if(data['message'] == 'success'){
                        $obj.attr("data-before", the_index);
                    }
                    else{
                        alert(data['message']);
                    }
                });
            }
        }
    }

    // 修改排序按钮事件
    $(".order_index>input").keyup(function(){
        edit_index($(this));
    });

    // 编辑banner按钮
    var current_banner_id = 0;
    var current_order_index = 1;
    $(".edit_banner_btn").click(function(){
        $("#pop_modal").click();
        $("#myModalLabel").text('编辑banner');
        var $obj = $(this).parents("tr:first");
        var banner_alt = $.trim($obj.find(".banner_alt").text());
        var banner_url = $.trim($obj.find(".banner_url").text());
        current_banner_id = $.trim($obj.find(".banner_id").text());
        current_order_index = $.trim($obj.find(".order_index>input").val());
        console.log(current_banner_id, current_order_index)
        $("#banner_url").val(banner_url);
        $("#banner_alt").val(banner_alt);
        var img = "<img style='margin-bottom:15px' class='img img-responsive' src='"+banner_url+"'>";
        $("#view_img").html('').append(img);
        $("#up_load_img").text("编辑");
    });

    // 上传图片按钮
    $("#up_load_img").click(function(){
        $("#my_file").click();
    });

    // 检测文件上传表单的变化
    $("#my_file").change(function(){
        $("#submit_img_button").click();
    });

    // 上传图片成功后
    $("#exec_target").load(function () {
        var data = $(window.frames['exec_target'].document.body).html();  //上传文件返回
        console.log(data);
        var val = $.trim(data);
        if(val.indexOf(".jpg") != -1 || val.indexOf(".png") != -1 || val.indexOf(".jpeg") != -1 ){
                $("#banner_url").val(val);
                var img = "<img style='margin-bottom:15px' class='img img-responsive' src='"+val+"'>";
                $("#view_img").html('').append(img);
                $("#up_load_img").text("编辑");
            }
            else if(val == ""){
            //nothing...
        }
        else{
                (data);
        }
    });

    // 提交新增/编辑 banner事件
    $("#banner_submit_btn").click(function(){
        var title = $("#myModalLabel").text();
        var banner_alt = $.trim($("#banner_alt").val());
        var banner_url = $.trim($("#banner_url").val());
        if(banner_url == ''){
            alert("你还没有上传图片");
            return false;
        }
        else{
            if(title == "添加banner"){
                // 添加banner的情况
                var args = {"banner_alt": banner_alt, "banner_url": banner_url};
                $.post("/manage_banner/add", args, function(data){
                    var data = JSON.parse(data);
                    if(data['message'] == 'success'){
                        alert("添加成功");
                        location.href = location.href;
                    }
                    else{
                        alert(data['message']);
                    }
                });
            }
            else{
                // 编辑banner的情况。
                var args = {"banner_alt": banner_alt, "banner_url": banner_url,
                    "banner_id": current_banner_id, "order_index": current_order_index};
                $.post("/manage_banner/edit", args, function(data){
                    var data = JSON.parse(data);
                    if(data['message'] == 'success'){
                        alert("编辑成功");
                        location.href = location.href;
                    }
                    else{
                        alert(data['message']);
                    }
                });
            }

        }
    });

    // 删除 banner
    $(".delete_banner_btn").click(function(){
        var banner_id = $.trim($(this).parents("tr:first").find(".banner_id").text());
        var r = confirm("你确实要删除当前的banner吗？");
        if(r){
            var args = {"banner_id": banner_id};
            $.post("/manage_banner/delete", args, function(data){
                var data = JSON.parse(data);
                if(data['message'] == 'success'){
                    alert("删除成功哦");
                    location.href = location.href;
                }
                else{
                    alert(data['message']);
                }
            });
        }
    });

    // 左侧导航
    $(".my_nav_item").click(function(){
        var text = $(this).text();
        console.log(text);
        $(".my_nav_item").not($(this)).removeClass("btn-primary");
        $(this).addClass("btn-primary");
        if(text.indexOf("anner") != -1){
            $("#banner_zone").show();
            $("#hot_word_zone").hide();
        }
        else{
            $("#banner_zone").hide();
            $("#hot_word_zone").show();
        }
    });

    // 点击文本显示编辑框
    $(".show_text").click(function(){
        var text = $.trim($(this).text());
        $(this).next(".edit_text").val(text).show();
        $(this).hide();
    });

    // 编辑文本按钮事件
    $(".edit_text_btn").click(function(){
        var $this = $(this).parents("tr:first");
        var text = $.trim($this.find(".show_text").text());
        $this.find(".edit_text").val(text).show();
        $this.find(".show_text").hide();
    });

    // 保存文本框事件
    $(".save_text_btn").click(function(){
        var $this =$(this).parents("tr:first");
        var text1 = $.trim($this.find(".edit_text").val());
        var text2 = $.trim($this.find(".show_text").text());
        if(text1 == text2){
            //nothing...
        }
        else if($this.find(".edit_text:visible").length == 0){
            // 编辑框被隐藏状态不执行
            $this.find(".edit_text").val('').hide();
            $this.find(".show_text").show();
        }
        else{
            var key_word_id = $.trim($this.find(".key_word_id").text());
            var args = {"key_word_id": key_word_id, "word_text": text1};
            $.post("/manage_keywords/edit", args, function(data){
                var data = JSON.parse(data);
                if(data['message'] == 'success'){
                    $this.find(".edit_text").val('').hide();
                    $this.find(".show_text").text(text1).show();
                }
                else{
                    alert(data['message']);
                }
            });
        }
    });

//end !
});
