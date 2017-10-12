$(function () {
    let btnScrollTop = $('#scroll-to-top');
    btnScrollTop.fadeOut(0);
    btnScrollTop.on('click', function () {
        let currentScrollTop = document.documentElement.scrollTop || window.pageYOffset || document.body.scrollTop;
        let time = 0.1875 * currentScrollTop + 125;
        time = time > 500 ? 500 : time;
        $('body,html').animate({
            scrollTop: 0
        }, time);
    });

    $(window).scroll(function(){
        let currentScrollTop = document.documentElement.scrollTop || window.pageYOffset || document.body.scrollTop;
        if (currentScrollTop > 400) {
            btnScrollTop.fadeIn(200);
        } else {
            btnScrollTop.fadeOut(200);
        }
    });
});