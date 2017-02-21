/**
 * Created by walle on 2017/1/26.
 */
$(function(){
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
        location.href = "#my_message";
        $("#my_message").focus();
    });

    //end!
});