# -*-coding:utf-8 -*-
import os
from datetime import datetime, timedelta

from qiniu import Auth, put_file, etag, BucketManager

import configs


class BackupTool(object):
    __LOCAL_FILE_DIRECTORY = configs.Config.DATABASE_BACKUP_FILE_DIRECTORY
    __KEY = 'celerysoft-science-%s.sql'
    __DATETIME_FORMAT = '%Y%m%d'

    __qiniu_instance = None

    def __init__(self):
        self.__qiniu_instance = Auth(configs.Config.QINIU_ACCESS_KEY, configs.Config.QINIU_SECRET_KEY)
        self.__qiniu_bucket_name = configs.Config.QINIU_BUCKET_NAME_FOR_BACKUP_DATABASE

    def execute(self):
        self.__upload()
        self.__delete_backup_30days_ago()

    def __upload(self):
        # 上传后保存的文件名
        # celerysoft-science-20190227.sql
        key = self.__KEY % datetime.now().strftime(self.__DATETIME_FORMAT)
        # 生成上传 Token，可以指定过期时间等
        token = self.__qiniu_instance.upload_token(self.__qiniu_bucket_name, key, 3600)
        # 要上传文件的本地路径
        local_file = os.path.join(self.__LOCAL_FILE_DIRECTORY, key)
        ret, info = put_file(token, key, local_file)

        try:
            assert ret['key'] == key
            assert ret['hash'] == etag(local_file)
            print('数据库备份上传到七牛成功')
        except AssertionError:
            print('数据库备份上传到七牛失败，请手动进行处理！！！')

    def __delete_backup_30days_ago(self):
        _30days_ago = datetime.now() - timedelta(days=20)
        key = self.__KEY % _30days_ago.strftime(self.__DATETIME_FORMAT)
        bucket = BucketManager(self.__qiniu_instance)

        ret, info = bucket.stat(configs.Config.QINIU_BUCKET_NAME, key)
        if ret is None or 'hash' not in ret:
            print('30天前的备份不存在，不需要删除')
        else:
            ret, info = bucket.delete(self.__qiniu_bucket_name, key)
            try:
                assert ret == {}
            except AssertionError:
                print('删除30天前的备份文件失败，请手动删除')


if __name__ == '__main__':
    t = BackupTool()
    t.execute()
