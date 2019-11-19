所有后台接口都位于`/application/views`目录内

## 路由规则

接口的路由根据接口类的文件路径来确认，例如：

`/application/views/transfer/appointment/confirmation.py`的URI为`/transfer/appointment/confirmation`

根目录的`config.py`文件里有个`BASE_URL`属性，代表URI前缀。

接口目录里通目录名称相同的文件的路由为`目录路径`，例如：

`/application/views/transfer/appointment/appointment.py`的URI为`/transfer/appointment`

`/application/views/transfer/transfer.py`的URI为`/transfer`

路由规则在`app.py`文件的`add_url_rules_and_register_blueprints`方法里定义，如有不解可以查看该段源码。

## 新建接口规则

接口路由见上一节`路由规则`，在此不再赘述。

### 创建子路由

假设需要创建一个URI为`/transfer/appointment/confirmation`在的接口，则首先需要创建目录`/application/views/transfer/appointment/`，在目录下创建一个文件`confirmation.py`。

```python
# -*- coding: utf-8 -*-
from application.views.base_api import BaseAPI, ApiResult
from flask import make_response

class AppointmentConfirmationAPI(BaseAPI):
    def get(self):
        result = ApiResult('Hello World', 200)
        return make_response(result.to_response())


bp_view = AppointmentConfirmationAPI
```

注意最后一行的`bp_view = AppointmentConfirmationAPI`，`bp_view`是将接口自动添加进路由的必要条件。

### 创建根路由

根路由和子路由有所区别，接上节子路由的内容，假设需要创建一个URI为`/transfer/appointment`的接口，正确的操作是在目录`/application/views/transfer/appointment/`下创建一个文件`appointment.py`。

> 错误的做法：在目录`/application/views/transfer/`下创建一个文件`appointment.py`，这么做是错误的，在设计的时候，我认为`/transfer/appointment`接口，和`/transfer/appointment/`下的子接口是有业务关联（或者说一致性），所以将这两者置于同一个目录内。

重复一遍，假设需要创建一个URI为`/transfer/appointment`的接口，正确的做法是在目录`/application/views/transfer/appointment/`下创建一个文件`appointment.py`。

```python
from app import derive_import_root, add_url_rules_for_blueprint
from application.views.base_api import BaseNeedLoginAPI, ApiResult
from flask import Blueprint, make_response

class AppointmentAPI(BaseNeedLoginAPI):
    def get(self):
        result = ApiResult('Hello World', 200)
        return make_response(result.to_response())


bp = Blueprint(__name__.split('.')[-1], __name__)
bp.add_url_rule('', view_func=AppointmentAPI.as_view(AppointmentAPI.__name__))

root = derive_import_root(__name__)
add_url_rules_for_blueprint(root, bp)
```

看最后四行，到这里应该就能看明白什么是根路由了，根路由是一个蓝图，子路由的规则都添加在蓝图下。