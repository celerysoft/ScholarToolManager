import exception


def check_user_permission(session):
    if 'user' not in session.keys():
        session['user'] = None

    if session['user'] is None:
        raise exception.Unauthorized('请先登录')
