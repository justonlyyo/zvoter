/**
 * Created by walle on 17-2-20.
 */
$(function(){
    // canvas指纹，用于识别匿名用户

    var canvas = document.createElement('canvas');
    var ctx = canvas.getContext('2d');
    var txt = 'http://security.voter.com/';
    ctx.textBaseline = "top";
    ctx.font = "14px 'Arial'";
    ctx.textBaseline = "voter";
    ctx.fillStyle = "#f60";
    ctx.fillRect(125,1,62,20);
    ctx.fillStyle = "#069";
    ctx.fillText(txt, 2, 15);
    ctx.fillStyle = "rgba(102, 204, 0, 0.7)";
    ctx.fillText(txt, 4, 17);
    var b64 = canvas.toDataURL().replace("data:image/png;base64,","");
    canvas_uuid = b64.slice(-32);
    var topic_id = $("#current_topic_id").text();
    $.get("/view_count?uuid="+Math.random()+"&canvas_uuid="+canvas_uuid+"&topic_id="+topic_id, function(data){
        //打开页面时，进行浏览计数
    });
    //end!
});