/**
 * Created by Administrator on 2017/1/17.
 */
$(function(){
    // 迷你菜单按钮
    var mini_menu_open = false;
    function close_min_nav(){
        $("#min_nav>li").not("#min_nav>li:first").css("display", "none");
        mini_menu_open = false;
    }
    function open_min_nav(){
        $("#min_nav>li").css("display", "block");
        mini_menu_open = true;
    }
    $("#min_nav .active>a").click(function(){
        if(!mini_menu_open){
            open_min_nav();
            return false;
        }
        else{
            close_min_nav();
            return false;
        }
    });
    $("body").not("#min_nav .active>a").click(function(){
        /*疑似废弃函数*/
        if(mini_menu_open){
            close_min_nav();
        }
    });

    /*迷你菜单相关函数应该都已经废止，仅做参考用。*/

    // 登录后，点击头像跳转用户中心
    $("#login_user_pic").click(function(){
        window.open("/user_center_info");
    });

    // 点击logo跳转到首页
    $(".to_index").click(function(){
        location.href = "/";
    });


    //end!
});