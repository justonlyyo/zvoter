/**
 * Created by zhouyi on 17-2-23.
 */
$(function () {
    /**
     * 用于实现通过点击我参与的、我发布的等按钮来切换不同话题的面板
     */

    $("#joined").click(function () {
        clearAll();
        $(this).addClass("active");
        $("#joined_panel").show();
    });

    $("#created").click(function () {
        clearAll();
        $(this).addClass("active");
        $("#created_panel").show();
    });

    function clearAll() {
        $("#joined").removeClass("active");
        $("#created").removeClass("active");
        $("#joined_panel").hide();
        $("#created_panel").hide();
    }

    // 初始状态默认为“我参与的”
    clearAll();
    $("#joined").click();
});