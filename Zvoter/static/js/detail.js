/**
 * Created by walle on 2017/1/26.
 */
$(function(){
    var login_flag = $.trim($("#login_flag").text()) == "1";  // 是否已登录

    // 小屏幕切换按钮
    $(".change_tips").click(function(){
        var $this = $(this);
        if($this.attr("class").indexOf("active") == -1){
            $(".change_tips").toggleClass("active");
            if($this.text().indexOf("A") != -1){
                $(".tips_blue").removeClass("hidden-xs").addClass("col-xs-12");
                $(".tips_red").removeClass("col-xs-12").addClass("hidden-xs");
            }
            else{
                $(".tips_red").removeClass("hidden-xs").addClass("col-xs-12");
                $(".tips_blue").removeClass("col-xs-12").addClass("hidden-xs");

            }
        }

    });

    // 我要评论的锚点
    $("#jump_edit_area").click(function(){
        if(!login_flag){
            window.open("/login");
        }
        else{
            location.href = "#my_message";
        }
    });

    // 优化进度条的样式
    function optimize_progress_bar(){
        var blue_obj = $(".blue_line");
        var red_obj = $(".red_line");
        var blue_num_str = $.trim(blue_obj.text().split("%")[0]);
        var red_num_str = $.trim(red_obj.text().split("%")[0]);
        var blue_num = parseFloat(blue_num_str);
        var red_num = parseFloat(red_num_str);
        var pattern = /^\d+\.0$/;  // 以.0结尾的

        if(pattern.test(blue_num_str) || pattern.test(red_num_str)){
            blue_num = parseInt(blue_num);
            red_num = parseInt(red_num);
        }else{}

        blue_obj.text(blue_num + "%");
        red_obj.text(red_num + "%");
        if(blue_num < 6){
            blue_obj.css("width", "6%");
            red_obj.css("width", "94%");
        }
        else if(red_num < 6){
            red_obj.css("width", "6%");
            blue_obj.css("width", "94%");
        }
        else{}
    }
    optimize_progress_bar();


    // 调整图片的高宽
    $(".img_a,.img_b").css("height", parseInt($(".voter_btn").css("width").split("px")[0])*0.75);

    //end!
});