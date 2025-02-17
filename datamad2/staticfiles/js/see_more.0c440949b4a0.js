$(".read-more").click(function (e) {
    e.preventDefault();
    var t = $(this);
    t.parent().find('.more').removeClass('d-none');
    t.addClass('d-none');

});


$(".more").click(function (e) {
    e.preventDefault();
    var t = $(this);
    t.parent().find('.read-more').removeClass('d-none');
    t.addClass('d-none');

});