/**
 * Created by walle on 2017/2/11.
 */
$(function () {
    // 检查是否重复
    function is_repeat(name) {
        // 检查是否重复
        var class_list = $(".small_class");
        var flag = true;
        for (var i = 0, l = class_list.length; i < l; i++) {
            var temp = $(class_list[i]);
            if (temp.text().toLowerCase() == name.toLowerCase()) {
                flag = false;
                alert(name + " 已存在");
                break;
            }
        }
        return flag;
    }

    /*添加类别按钮*/
    $(".add_class").click(function () {
        var name = prompt("请输入类别名");
        var $this = $(this);

        if (name) {
            // 检查是否重复
            name = $.trim(name);
            var flag = is_repeat(name);
            if (flag) {
                var channel_id = $this.parents(".channel:first").find("td:first").attr("data-id");
                var html = '<button class="btn btn-sm" type="button"><span data-channel-id="' + channel_id + '" data-class-id=""  onclick="show_edit($(this))" ' +
                    'class="small_class">' + name + '</span><span onclick="show_drop($(this))" class="drop_btn glyphicon glyphicon-remove-sign"></span></button>';
                $this.parent().append(html);
            }

        }
    });

    // 显示删除提示。
    show_drop = function ($obj) {
        var $obj = $obj.prev(".small_class");
        var con = confirm("你确定要删除 '" + $obj.text() + "' 这个小类吗？");
        console.log($(this).prev(".small_class").parents(".btn-sm:first"));
        if (con) {
            $obj.parents(".btn-sm:first").remove();
        } else {
        }
    };

    // 编辑小类
    show_edit = function ($obj) {
        var name = prompt("修改类别 '" + $obj.text() + "' 名称");
        if (name) {
            // 检查是否重复
            name = $.trim(name);
            if(!is_repeat(name)){
                alert("类别名重复");
            }
            else{
                $obj.text(name);
            }
        }
    };

    // 保存列别信息
    $("#save").click(function(){
        var class_list = {};
        $(".small_class").each(function(){
            var name = $(this).text();
            var channel_id = $(this).attr("data-channel-id");
            var class_id = $(this).attr("data-class-id");
            class_list[name] = JSON.stringify({"class_id": class_id, "channel_id": channel_id});
        });

        $.post("/manage_class/save", class_list, function(data){
            var data = JSON.parse(data);
            alert(data['message']);
            if(data['message'] == "success"){
                location.reload();
            }
        });
    });

    //end!
});
