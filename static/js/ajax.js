/**
 *
 * @param method HTTP方法
 * @param url 请求地址
 * @param data 请求数据
 * @param contentType 请求数据类型
 * @param callback 回调
 * @private
 */
function _httpJSON(method, url, data, contentType, callback) {
    let option = {
        type: method,
        dataType: 'json',
        withCredentials: true
    };
    if (method === 'GET') {
        option.url = url + '?' + data;
    } else if (method === 'POST' || method === 'PUT' || method === 'PATCH' || method === 'DELETE') {
        option.url = url;
        option.data = JSON.stringify(data || {});
        option.contentType = contentType ? contentType : 'application/json';
    }
    $.ajax(option)
        .done(function (data, textStatus, jqXHR) {
            return callback(null, data, jqXHR);
        })
        .fail(function (jqXHR, textStatus, errorThrown) {
            let message;
            try {
                let response = JSON.parse(jqXHR.responseText);
                message = response.message;
            } catch (e) {
                message = jqXHR.responseText
            }
            return callback({
                'code': jqXHR.status,
                'textStatus': textStatus,
                'errorThrown': errorThrown,
                'message': message
            }, null, jqXHR);
        });
}

/**
 *
 * @param url
 * @param data
 * @param callback
 */
function httpGet(url, data, callback) {
    if (arguments.length === 2) {
        callback = data;
        data = {};
    }
    if (typeof (data) === 'object') {
        let arr = [];
        $.each(data, function (k, v) {
            arr.push(k + '=' + encodeURIComponent(v));
        });
        data = arr.join('&');
    }
    _httpJSON('GET', url, data, null, callback);
}

/**
 *
 * @param url
 * @param data
 * @param callback
 * @param contentType
 */
function httpPost(url, data, callback, contentType) {
    _httpBase('POST', url, data, callback, contentType);
}

function httpDelete(url, data, callback, contentType) {
    _httpBase('DELETE', url, data, callback, contentType);
}

function httpPut(url, data, callback, contentType) {
    _httpBase('PUT', url, data, callback, contentType);
}

function httpPatch(url, data, callback, contentType) {
    _httpBase('PATCH', url, data, callback, contentType);
}

function _httpBase(method, url, data, callback, contentType) {
    if (arguments.length === 2) {
        callback = data;
        data = {};
    }
    _httpJSON(method, url, data, contentType, callback);
}

$(function () {
    $.fn.extend({
        httpPost: function (url, data, callback, contentType) {
            if (arguments.length === 2) {
                callback = data;
                data = {};
            }
            return this.each(function () {
                // let $form = $(this);
                // $form.showFormError();
                // $form.showFormLoading(true);
                _httpJSON('POST', url, data, contentType, function (error, data, jqXHR) {
                    // if (error) {
                    //     $form.showFormError(err);
                    //     $form.showFormLoading(false);
                    // }
                    callback && callback(error, data, jqXHR);
                });
            });
        }
    });
});