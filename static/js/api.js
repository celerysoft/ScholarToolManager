class Api {
    static _getApi(url, data, callback) {
        if (arguments.length === 2) {
            callback = data;
            data = {};
        }

        httpGet(url, data, function (error, data, jqXHR) {
            callback(error, data, jqXHR);
        });
    }

    static _postApi(url, data, callback) {
        httpPost(url, data, function (error, data, jqXHR) {
            callback(error, data, jqXHR);
        });
    }

    static _patchApi(url, data, callback) {
        httpPatch(url, data, function (error, data, jqXHR) {
            callback(error, data, jqXHR);
        });
    }

    static _putApi(url, data, callback) {
        httpPut(url, data, function (error, data, jqXHR) {
            callback(error, data, jqXHR);
        });
    }

    static _deleteApi(url, data, callback) {
        httpDelete(url, data, function (error, data, jqXHR) {
            callback(error, data, jqXHR);
        });
    }

    /**
     *
     * @param callback
     */
    static getTodayInHistory(callback) {
        this._getApi(this.TODAY_IN_HISTORY_URL, callback);
    }

    /**
     *
     * @param gReCaptchaResponse
     * @param callback
     */
    static verifyGoogleReCaptcha(gReCaptchaResponse, callback) {
        this._postApi(this.RE_CAPTCHA_URL, {response: gReCaptchaResponse}, callback);
    }

    /**
     * login
     * @param name username or email
     * @param password
     * @param callback
     */
    static login(name, password, callback) {
        this._postApi(this.LOGIN_URL, {
            name: name,
            password: password
        }, callback);
    }

    /**
     *
     * @param username
     * @param email
     * @param password
     * @param invitationCode
     * @param callback
     */
    static register(username, email, password, invitationCode, callback) {
        this._postApi(this.REGISTER_URL, {
            name: username,
            email: email,
            password: password,
            invitation_code: invitationCode
        }, callback);
    }

    /**
     *
     * @param userId
     * @param roleId
     * @param callback
     */
    static updateUserRole(userId, roleId, callback) {
        this._patchApi(this.USER_URL, {user_id: userId, role_id: roleId}, callback);
    }

    /**
     *
     * @param callback
     */
    static createInvitationCode(callback) {
        this._postApi(this.INVITATION_URL, null, callback);
    }

    /**
     *
     * @param userId
     * @param callback
     */
    static getUserPermissions(userId, callback) {
        this._getApi(this.PERMISSION_URL, {user_id: userId}, callback);
    }

    /**
     *
     * @param roleId
     * @param callback
     */
    static getRolePermissions(roleId, callback) {
        this._getApi(this.PERMISSION_URL, {role_id: roleId, all_permissions: true}, callback);
    }

    /**
     *
     * @param callback
     */
    static getPermissions(callback) {
        this._getApi(this.PERMISSION_URL, callback);
    }

    /**
     *
     * @param eventId
     * @param callback
     */
    static getEvent(eventId, callback) {
        this._getApi(this.EVENT_URL, {id: eventId}, callback);
    }

    /**
     *
     * @param name
     * @param tag
     * @param summary
     * @param content
     * @param callback
     */
    static createEvent(name, tag, summary, content, callback) {
        this._postApi(this.EVENT_URL, {
            name: name,
            tag: tag,
            summary: summary,
            content: content
        }, callback);
    }

    /**
     *
     * @param id
     * @param name
     * @param tag
     * @param summary
     * @param content
     * @param callback
     */
    static updateEvent(id, name, tag, summary, content, callback) {
        this._patchApi(this.EVENT_URL, {
            id: id,
            name: name,
            tag: tag,
            summary: summary,
            content: content
        }, callback);
    }

    /**
     *
     * @param eventId
     * @param callback
     */
    static deleteEvent(eventId, callback) {
        this._deleteApi(this.EVENT_URL, {id: eventId}, callback);
    }

    /**
     * get user role by user id
     * @param userId
     * @param callback
     */
    static getUserRole(userId, callback) {
        this._getApi(this.ROLE_URL, {user_id: userId}, callback);
    }

    /**
     *
     * @param name
     * @param label
     * @param description
     * @param permissions
     * @param callback
     */
    static createRole(name, label, description, permissions, callback) {
        this._postApi(this.ROLE_URL, {
            name: name,
            label: label,
            description: description,
            permissions: permissions
        }, callback);
    }

    /**
     *
     * @param roleId
     * @param name
     * @param label
     * @param description
     * @param permissions
     * @param callback
     */
    static updateRole(roleId, name, label, description, permissions, callback) {
        this._patchApi(this.ROLE_URL, {
            id: roleId,
            name: name,
            label: label,
            description: description,
            permissions: permissions
        }, callback);
    }

    /**
     *
     * @param roleId
     * @param callback
     */
    static deleteRole(roleId, callback) {
        this._deleteApi(this.ROLE_URL, {id: roleId}, callback);
    }


    /**
     *
     * @param templateId
     * @param callback
     */
    static getServiceTemplate(templateId, callback) {
        this._getApi(this.SERVICE_TEMPLATE_URL, {id:templateId}, callback);
    }

    /**
     *
     * @param callback
     */
    static getUsages(callback) {
        this._getApi(this.USAGE_URL, callback);
    }

    /**
     *
     * @param callback
     */
    static restartListenerServer(callback) {
        this._putApi(this.USAGE_URL, null, callback);
    }

    /**
     *
     * @param type
     * @param title
     * @param subtitle
     * @param description
     * @param balance
     * @param price
     * @param initialization_fee
     * @param callback
     */
    static createServiceTemplate(type, title, subtitle, description, balance, price, initialization_fee, callback) {
        this._postApi(this.SERVICE_TEMPLATE_URL, {
            type: type,
            title: title,
            subtitle: subtitle,
            description: description,
            balance: balance,
            price: price,
            initialization_fee: initialization_fee
        }, callback);
    }

    /**
     *
     * @param templateId
     * @param type
     * @param title
     * @param subtitle
     * @param description
     * @param balance
     * @param price
     * @param initialization_fee
     * @param callback
     */
    static updateServiceTemplate(templateId, type, title, subtitle, description, balance, price, initialization_fee, callback) {
        this._patchApi(this.SERVICE_TEMPLATE_URL, {
            id: templateId,
            type: type,
            title: title,
            subtitle: subtitle,
            description: description,
            balance: balance,
            price: price,
            initialization_fee: initialization_fee
        }, callback);
    }

    /**
     *
     * @param templateId
     * @param callback
     */
    static deleteServiceTemplate(templateId, callback) {
        this._deleteApi(this.SERVICE_TEMPLATE_URL, {id:templateId}, callback);
    }

    /**
     *
     * @param userId
     * @param page
     * @param pageSize
     * @param callback
     */
    static getUserService(userId, page, pageSize, callback) {
        this._getApi(this.SERVICE_URL, {
            user_id: userId,
            page: page,
            page_size: pageSize
        }, callback);
    }

    /**
     *
     * @param serviceId
     * @param callback
     */
    static getService(serviceId, callback) {
        this._getApi(this.SERVICE_URL, {id: serviceId}, callback);
    }

    /**
     *
     * @param templateId
     * @param password
     * @param autoRenew
     * @param callback
     */
    static createService(templateId, password, autoRenew, callback) {
        let data;
        if (autoRenew !== null) {
            data = {
                template_id: templateId,
                password: password,
                auto_renew: autoRenew
            }
        } else {
            data = {
                template_id: templateId,
                password: password
            }
        }

        this._postApi(this.SERVICE_URL, data, callback);
    }

    /**
     *
     * @param serviceId
     * @param autoRenew
     * @param callback
     */
    static renewService(serviceId, autoRenew, callback) {
        let data = {
            id: serviceId,
            renew: true
        };
        if (autoRenew !== null) {
            data['auto_renew'] = autoRenew;
        }

        this._patchApi(this.SERVICE_URL, data, callback);
    }

    /**
     *
     * @param serviceId
     * @param autoRenew
     * @param callback
     */
    static modifyAutoRenewForService(serviceId, autoRenew, callback) {
        this._patchApi(this.SERVICE_URL, {id: serviceId, auto_renew: autoRenew}, callback);
    }

    /**
     *
     * @param userId
     * @param callback
     */
    static getUserScholarBalance(userId, callback) {
        this._getApi(this.SCHOLAR_BALANCE_URL, {user_id: userId}, callback);
    }

    /**
     *
     * @param userId
     * @param amount
     * @param callback
     */
    static rechargeUserScholarBalance(userId, amount, callback) {
        this._patchApi(this.SCHOLAR_BALANCE_URL, {user_id: userId, amount: amount}, callback);
    }

    /**
     *
     * @param serviceId
     * @param newPassword
     * @param callback
     */
    static updateServicePassword(serviceId, newPassword, callback) {
        this._patchApi(this.SERVICE_PASSWORD_URL, {service_id: serviceId, new_password: newPassword}, callback)
    }
}

// Third-party api
Api.GOOGLE_RE_CAPTCHA = 'https://www.recaptcha.net/recaptcha/api.js';

// api
Api.RE_CAPTCHA_URL = BASE_URL + 'grecaptcha';
Api.TODAY_IN_HISTORY_URL = BASE_URL + 'today-in-history';
Api.LOGIN_URL = BASE_URL + 'login';
Api.REGISTER_URL = BASE_URL + 'register';
Api.USER_URL = BASE_URL + 'user';
Api.INVITATION_URL = BASE_URL + 'invitation';
Api.PERMISSION_URL = BASE_URL + 'permission';
Api.EVENT_URL = BASE_URL + 'event';
Api.ROLE_URL = BASE_URL + 'role';
Api.SERVICE_TEMPLATE_URL = BASE_URL + 'service-template';
Api.SERVICE_URL = BASE_URL + 'service';
Api.USAGE_URL = BASE_URL + 'usage';
Api.SCHOLAR_BALANCE_URL = BASE_URL + 'scholar-balance';
Api.SERVICE_PASSWORD_URL = BASE_URL + 'service-password';

