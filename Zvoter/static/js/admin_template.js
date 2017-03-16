/**
 * Created by walle on 2017/2/11.
 */
$(function(){
    /*根据href确定哪一个导航标签被激活*/
    var url = location.href;
    $("li[role='presentation']").each(function(){
        var $this = $(this);
        if(url.indexOf($this.find("a").attr("href")) != -1){
            $this.addClass("active");
        }
    });

    // 根据状态获取颜色
    get_color = function (status_str){
        var status = parseInt(status_str);
        var color = "";
        switch (status){
            case 0:
                color = "#ffc20e";
                break;
            case -1:
                color = "#72777b";
                break;
            case 1:
                color = "#007d65";
                break;
            case 2:
                color = "#d71345";
                break;
            default:
                color = "black";
        }
        return color;
    };


    //end!
});
