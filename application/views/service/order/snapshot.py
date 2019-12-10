# -*- coding: utf-8 -*-
from application import exception
from application.model.subscribe_service_snapshot import SubscribeServiceSnapshot
from application.util.database import session_scope
from application.views.base_api import BaseNeedLoginAPI, ApiResult


class ServiceOrderSnapshotAPI(BaseNeedLoginAPI):
    methods = ['GET']

    def get(self):
        with session_scope() as session:
            snapshot_list = []
            snapshots = self.derive_query_for_get_method(session, SubscribeServiceSnapshot) \
                .filter(SubscribeServiceSnapshot.user_uuid == self.user_uuid).all()
            for snapshot in snapshots:  # type: SubscribeServiceSnapshot
                snapshot_list.append(snapshot.to_dict())

            payload = {}
            if len(snapshot_list) == 0:
                raise exception.api.NotFound('订单快照不存在')
            elif len(snapshot_list) == 1:
                payload['snapshot'] = snapshot_list.pop()
            else:
                payload['snapshots'] = snapshot_list

            result = ApiResult('获取订单快照信息成功', payload=payload)
            return result.to_response()


view = ServiceOrderSnapshotAPI
