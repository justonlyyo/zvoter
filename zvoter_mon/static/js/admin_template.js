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

    //end!
});
