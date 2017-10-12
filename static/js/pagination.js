$(function () {
    $('#pagination-btn-jump').click(function () {
        let page = $('#pagination-input-page').val();
        let url = location.pathname;
        return location.assign(url + '?page=' + page);
    });
});


