/**
 * Created by walle on 2017/1/24.
 */
$(function(){
    // 调整发起投票高度
    // 第一个参数是被调整的对象，第二个参数是参照的对象
    function re_size(obj1, obj2){
        var nav_line = obj2;
        var nav_length = nav_line.height();
        obj1.css({"height": nav_length,
            "line-height": nav_length+"px",
            "padding-top":"0px"
        });
    }
    re_size($("#voter_btn_big"), $(".my_nav"));

    function re_size2(){
        var $obj1 = $("#voter_btn_small");
        var height = $(".my_nav ").height() - $(".blue_right").height();
        console.log(height)
        $obj1.css({"height": height/2,
            "line-height": height/2+"px",
            "margin-top":"20px"
        });
    }
    re_size2();

    $(window).resize(function(){
        re_size($("#voter_btn_big"), $(".my_nav"));
    });


    //end!
});