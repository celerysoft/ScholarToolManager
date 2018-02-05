let $$ = mdui.JQ;

/**
 * 设置文档主题
 */
(function () {
    const DEFAULT_PRIMARY = 'indigo';
    const DEFAULT_ACCENT = 'red';
    const DEFAULT_LAYOUT = '';

    const PRIMARY_COOKIE_KEY = 'scholar-theme-primary';
    const ACCENT_COOKIE_KEY = 'scholar-theme-accent';
    const LAYOUT_COOKIE_KEY = 'scholar-theme-layout';


    // 设置 cookie
    let setCookie = function (key, value) {
        // cookie 有效期为 1 年
        let date = new Date();
        date.setTime(date.getTime() + 365 * 24 * 3600 * 1000);
        document.cookie = key + '=' + value + '; expires=' + date.toGMTString() + '; path=/';
    };

    let getCookie = function (key) {
        let arr, reg = new RegExp("(^| )" + key + "=([^;]*)(;|$)");

        if (arr = document.cookie.match(reg))

            return unescape(arr[2]);
        else
            return null;
    };

    let setDocsTheme = function (theme) {
        if (typeof theme.primary === 'undefined') {
            theme.primary = false;
        }
        if (typeof theme.accent === 'undefined') {
            theme.accent = false;
        }
        if (typeof theme.layout === 'undefined') {
            theme.layout = false;
        }

        let i, len;
        let $body = $$('body');

        let classStr = $body.attr('class');
        let classs = classStr.split(' ');

        // 设置主色
        if (theme.primary !== false) {
            for (i = 0, len = classs.length; i < len; i++) {
                if (classs[i].indexOf('mdui-theme-primary-') === 0) {
                    $body.removeClass(classs[i])
                }
            }
            $body.addClass('mdui-theme-primary-' + theme.primary);
            setCookie(PRIMARY_COOKIE_KEY, theme.primary);
            $$('input[name="doc-theme-primary"][value="' + theme.primary + '"]').prop('checked', true);
        }

        // 设置强调色
        if (theme.accent !== false) {
            for (i = 0, len = classs.length; i < len; i++) {
                if (classs[i].indexOf('mdui-theme-accent-') === 0) {
                    $body.removeClass(classs[i]);
                }
            }
            $body.addClass('mdui-theme-accent-' + theme.accent);
            setCookie(ACCENT_COOKIE_KEY, theme.accent);
            $$('input[name="doc-theme-accent"][value="' + theme.accent + '"]').prop('checked', true);
        }

        // 设置主题色
        if (theme.layout !== false) {
            for (i = 0, len = classs.length; i < len; i++) {
                if (classs[i].indexOf('mdui-theme-layout-') === 0) {
                    $body.removeClass(classs[i]);
                }
            }
            if (theme.layout !== '') {
                $body.addClass('mdui-theme-layout-' + theme.layout);
            }
            setCookie(LAYOUT_COOKIE_KEY, theme.layout);
            $$('input[name="doc-theme-layout"][value="' + theme.layout + '"]').prop('checked', true);
        }
    };

    // 切换主色
    $$(document).on('change', 'input[name="doc-theme-primary"]', function () {
        setDocsTheme({
            primary: $$(this).val()
        });
    });

    // 切换强调色
    $$(document).on('change', 'input[name="doc-theme-accent"]', function () {
        setDocsTheme({
            accent: $$(this).val()
        });
    });

    // 切换主题色
    $$(document).on('change', 'input[name="doc-theme-layout"]', function () {
        setDocsTheme({
            layout: $$(this).val()
        });
    });

    // 恢复默认主题
    $$(document).on('cancel.mdui.dialog', '#dialog-docs-theme', function () {
        setDocsTheme({
            primary: DEFAULT_PRIMARY,
            accent: DEFAULT_ACCENT,
            layout: DEFAULT_LAYOUT
        });
    });

    $$(function () {
        let hasCookie = false;

        let primaryCookie = getCookie(PRIMARY_COOKIE_KEY);
        if (!isNull(primaryCookie)) {
            hasCookie = true;
        }
        let accentCookie = getCookie(ACCENT_COOKIE_KEY);
        if (!isNull(accentCookie)) {
            hasCookie = true;
        }
        let layoutCookie = getCookie(LAYOUT_COOKIE_KEY);
        if (!isNull(layoutCookie)) {
            hasCookie = true;
        }

        if (hasCookie) {
            primaryCookie = isNull(primaryCookie) ? DEFAULT_PRIMARY : primaryCookie;
            accentCookie = isNull(accentCookie) ? DEFAULT_PRIMARY : accentCookie;
            layoutCookie = isNull(layoutCookie) ? DEFAULT_PRIMARY : layoutCookie;
        }

        if (hasCookie) {
            setDocsTheme({
                primary: primaryCookie,
                accent: accentCookie,
                layout: layoutCookie
            });
        } else {
            setDocsTheme({
                primary: DEFAULT_PRIMARY,
                accent: DEFAULT_ACCENT,
                layout: DEFAULT_LAYOUT
            });
        }
    });
})();

$(function () {
    $.fn.extend({
        showFormError: function (err) {
            return this.each(function () {
                let
                    $form = $(this),
                    $alert = $form && $form.find('.uk-alert-danger'),
                    fieldName = err && err.data;
                if (!$form.is('form')) {
                    console.error('Cannot call showFormError() on non-form object.');
                    return;
                }
                $form.find('input').removeClass('uk-form-danger');
                $form.find('select').removeClass('uk-form-danger');
                $form.find('textarea').removeClass('uk-form-danger');
                if ($alert.length === 0) {
                    console.warn('Cannot find .uk-alert-danger element.');
                    return;
                }
                if (err) {
                    $alert.text(err.message ? err.message : (err.error ? err.error : err)).removeClass('uk-hidden').show();
                    if (($alert.offset().top - 60) < $(window).scrollTop()) {
                        $('html,body').animate({scrollTop: $alert.offset().top - 60});
                    }
                    if (fieldName) {
                        $form.find('[name=' + fieldName + ']').addClass('uk-form-danger');
                    }
                }
                else {
                    $alert.addClass('uk-hidden').hide();
                    $form.find('.uk-form-danger').removeClass('uk-form-danger');
                }

                mdui.snackbar({
                    message: err.message ? err.message : (err.error ? err.error : err)
                });
            });
        },
        showFormLoading: function (isLoading) {
            return this.each(function () {
                let
                    $form = $(this),
                    $submit = $form && $form.find('button[type=submit]'),
                    $buttons = $form && $form.find('button');
                $i = $submit && $submit.find('i'),
                    iconClass = $i && $i.attr('class');
                if (!$form.is('form')) {
                    console.error('Cannot call showFormLoading() on non-form object.');
                    return;
                }
                if (!iconClass || iconClass.indexOf('uk-icon') < 0) {
                    console.warn('Icon <i class="uk-icon-*>" not found.');
                    return;
                }
                if (isLoading) {
                    $buttons.attr('disabled', 'disabled');
                    $i && $i.addClass('uk-icon-spinner').addClass('uk-icon-spin');
                }
                else {
                    $buttons.removeAttr('disabled');
                    $i && $i.removeClass('uk-icon-spinner').removeClass('uk-icon-spin');
                }
            });
        }
    });
});

function isNull(str) {
    return str === null || str === 'null' || str === 'undefined'
}

function redirect(url) {
    let
        hash_pos = url.indexOf('#'),
        query_pos = url.indexOf('?'),
        hash = '';
    if (hash_pos >= 0) {
        hash = url.substring(hash_pos);
        url = url.substring(0, hash_pos);
    }
    url = url + (query_pos >= 0 ? '&' : '?') + 't=' + new Date().getTime() + hash;
    console.log('redirect to: ' + url);
    location.assign(url);
}

function refresh() {
    let
        t = new Date().getTime(),
        url = location.pathname;
    if (location.search) {
        url = url + location.search + '&t=' + t;
    }
    else {
        url = url + '?t=' + t;
    }
    location.assign(url);
}

/**
 * 将时间戳转换为智能时间
 * @param timestamp python时间戳
 * @returns {String} 时间
 */
function toSmartDate(timestamp) {
    if (typeof(timestamp) === 'string') {
        timestamp = parseInt(timestamp);
    }
    if (isNaN(timestamp)) {
        return '';
    }

    // python的timestamp需要乘1000
    timestamp *= 1000;

    const
        MINUTE = 60 * 1000,
        HOUR = 60 * MINUTE,
        DAY = 24 * HOUR,
        MONTH = 30 * DAY;


    let
        today = new Date(),
        now = today.getTime(),
        result = '1分钟前',
        deltaTime = now - timestamp;
    if (deltaTime > MONTH) {
        // more than a month:
        let that = new Date(timestamp);
        let
            y = that.getFullYear(),
            m = that.getMonth() + 1,
            d = that.getDate(),
            hh = that.getHours(),
            mm = that.getMinutes();
        result = y === today.getFullYear() ? '' : y + '年';
        result = result + m + '月' + d + '日 ' + hh + ':' + (mm < 10 ? '0' : '') + mm;
    } else if (deltaTime >= DAY) {
        // 1-30 days ago:
        result = Math.floor(deltaTime / DAY) + '天前';
    } else if (deltaTime >= HOUR) {
        // 1-23 hours ago:
        result = Math.floor(deltaTime / HOUR) + '小时前';
    } else if (deltaTime >= MINUTE) {
        // 1-59 minutes age:
        result = Math.floor(deltaTime / MINUTE) + '分钟前';
    }

    return result;
}

function timestampToDateString(timestamp) {
    let date = new Date(timestamp);
    return dateToDateString(date);
}

function dateStringToDateString(date) {
    let d = new Date(date);
    return dateToDateString(d);
}

function dateToDateString(date) {
    let
        y = date.getUTCFullYear(),
        m = date.getUTCMonth() + 1,
        d = date.getUTCDate(),
        hh = date.getUTCHours(),
        mm = date.getUTCMinutes();
    return y + '年' + m + '月' + d + '日 ' + (hh < 10 ? '0' : '') + hh + ':' + (mm < 10 ? '0' : '') + mm;
}

function encodeHtml(str) {
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');
}

function unicodeToChinese(unicodeStr) {
    return unescape(unicodeStr.replace(/\\u/g, '%u'));
}

