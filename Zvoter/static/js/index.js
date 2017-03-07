/**
 * Created by Administrator on 2017/1/18.
 */
$(function(){
    // 初始化banner
    $(function(){
        $('.my-slider').unslider({delay: 5000,
      dots: true,autoplay:true,
      fluid: true});
    });

    // 调整发起投票高度
    function re_size(){
        var screen_width = $(window).width();
        var btn = $(".vote_btn_big>a");
        var nav_line = $("#my_nav .nav_line");
        var nav_length = $("#my_nav").height();

        if(screen_width > 680){
            $(".vote_btn_big").css({"height": nav_length,
            "line-height": nav_length+"px",
            "padding-top":"0px"
            });
            if(btn.html() != "发起投票"){
                btn.html("发起投票");
                btn.css({"margin-top":"0px","letter-spacing":"normal"});
            }
            nav_line.css("padding-left","1em");
        }
        else{
             $(".vote_btn_big").css({"height": nav_length,
            "line-height": "30px",
            "padding-top":"0px"
            });
            if(btn.html() != "发起<br>投票"){
                btn.html("发起<br>投票");
            }
            btn.css({"margin-top":(nav_length-btn.height())/2+"px","letter-spacing":"10px"});
            nav_line.css("padding-left","0");
        }

    }
    re_size();
    $(window).resize(function(){
        re_size();
    });
    //end
});
