/**
 * Created by zhouyi on 17-3-6.
 */
$(function () {
    // 将通知标为已读
    $(".mark_as_read").click(function () {
        var info=$(this).siblings().filter(".notification_info");
        var no_id=info.children().filter(".notification_id").text();
        var detail=$(this).siblings().filter(".detail_unread");
        var mark_button=$(this);
        $.post("/mark_notification/"+no_id, function (data) {
            // alert(data.message)
            var data = JSON.parse(data);
            // alert(data.message)
            if (data['message'] == 'successful') {
                detail.removeClass("detail_unread");
                detail.addClass("detail_read");
                mark_button.remove();
            }
        });
    });
});