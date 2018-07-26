# -*-coding:utf-8 -*-
import hashlib
import os
import re
import shutil

from qiniu import Auth, BucketManager, build_batch_rename, put_file

import configs


def derive_hash_filename(filename: str):
    project_root_path = configs.Config.BASE_DIR
    filename_splits = os.path.splitext(filename)

    hash_str = derive_file_md5(project_root_path + filename)

    if len(filename_splits) == 2:
        hashed_filename = '%s_%s' % (filename_splits[0], hash_str) + filename_splits[1]
    else:
        raise RuntimeError()

    static_root_path = os.path.abspath((os.path.join(configs.Config.STATIC_ROOT, '../')))
    copy_file(project_root_path + filename, static_root_path + hashed_filename)

    return hashed_filename


def generate_hashed_filename(filename):
    """

    :param filename:
    :return:
    """
    if os.path.isabs(filename):
        abs_filename = filename
        filename = os.path.split(filename)[1]
    else:
        abs_filename = configs.Config.BASE_DIR + filename

    hash_str = derive_file_md5(abs_filename)

    filename_splits = os.path.splitext(filename)

    if len(filename_splits) == 2:
        hashed_filename = '%s_%s' % (filename_splits[0], hash_str) + filename_splits[1]
    else:
        raise RuntimeError()

    return hashed_filename


def derive_file_md5(filename):
    BUF_SIZE = 65536
    md5 = hashlib.md5()

    with open(filename, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            md5.update(data)

    return md5.hexdigest()


def copy_file(src, dst, print_log=False):
    if not os.path.exists(dst):
        if not os.path.exists(os.path.dirname(dst)):
            mkdir_for_file(dst)

        if print_log:
            print('copy file %s to %s' % (src, dst))
        shutil.copyfile(src, dst)
        return True
    else:
        if print_log:
            print('pass duplicate file: %s' % dst)
        return False


def mkdir_for_file(dst):
    dst = os.path.normpath(dst)
    dirname = os.path.dirname(dst)
    dirnames = dirname.split(os.sep)

    dirname = os.sep
    for i in range(len(dirnames)):
        dirname = os.path.join(dirname, dirnames[i])
        if not os.path.exists(dirname):
            print('mkdir: %s' % dirname)
            os.mkdir(dirname)


class Command(object):
    access_key = configs.Config.QINIU_ACCESS_KEY
    secret_key = configs.Config.QINIU_SECRET_KEY
    bucket_name = configs.Config.QINIU_BUCKET_NAME

    SLASH_SUBSTITUTE_BY = '####'
    exclude_files = [
        r'/static/js/jquery-3.2.1.min.map',
        r'/static/js/jquery-3.2.1.js',
        r'/static/js/mdui.js',
        r'/static/js/vue.js',
        r'/static/css/font-awesome.css',
        r'/static/css/mdui.css',
        r'.DS_Store'
    ]
    exclude_paths = [
        r'^[-/\w]+?/static/fonts$',
        r'^[-/\w]+?/static/icons$',
        r'^[-/\w]+?/static/image$'
    ]

    def execute(self, generate_type):
        src = os.path.join(configs.Config.BASE_DIR, 'static')
        self.__iterate_then_generate(src, generate_type=generate_type)
        if generate_type == 0:
            self.rename_static_file_in_cdn()

    def __iterate_then_generate(self, path, generate_type=0):
        if not os.path.isabs(path):
            path = os.path.abspath(path)

        if os.path.isfile(path):
            for exclude_file in self.exclude_files:
                if self.__match(exclude_file, path):
                    print('pass exclude file: %s' % path)
                    return
            if generate_type == 0:
                static_file_path = self.__generate_static_resource_for_uploading_to_cdn(path)
                if static_file_path is not None:
                    self.__upload_static_resource_to_cdn(static_file_path)
            else:
                self.__generate_static_resource_for_local_serving(path)
            return
        else:
            for exclude_path in self.exclude_paths:
                if self.__match(exclude_path, path):
                    print('pass exclude path: %s' % path)
                    return
            print('enter path: %s' % path)
            for x in os.listdir(path):
                self.__iterate_then_generate(os.path.join(path, x), generate_type=generate_type)

    @staticmethod
    def __generate_static_resource_for_uploading_to_cdn(filename):
        hashed_filename = generate_hashed_filename(filename)

        relpath = os.path.relpath(filename, configs.Config.BASE_DIR)
        filename_splits = os.path.split(relpath)
        if len(filename_splits) == 2:
            hashed_filename = '%s/%s' % (filename_splits[0], hashed_filename)
        else:
            raise RuntimeError()

        hashed_filename = hashed_filename.replace(os.path.sep, Command.SLASH_SUBSTITUTE_BY)

        dst = os.path.join(configs.Config.CDN_STATIC_ROOT, hashed_filename)
        copy_file_success = copy_file(filename, dst, print_log=True)

        return dst if copy_file_success else None

    @staticmethod
    def __generate_static_resource_for_local_serving(filename):
        hashed_filename = generate_hashed_filename(filename)

        relpath = os.path.relpath(filename, configs.Config.BASE_DIR)
        filename_splits = os.path.split(relpath)
        if len(filename_splits) == 2:
            hashed_filename = '%s/%s' % (filename_splits[0], hashed_filename)
        else:
            raise RuntimeError()

        static_root_path = os.path.abspath(os.path.dirname(configs.Config.STATIC_ROOT))
        copy_file(filename, os.path.join(static_root_path, hashed_filename), print_log=False)

    @staticmethod
    def __match(pattern, string: str):
        if re.match(pattern, string) is not None:
            return True
        else:
            return string.find(pattern) > -1

    def __upload_static_resource_to_cdn(self, file_path: str):
        print('upload %s to cdn' % file_path)
        # 构建鉴权对象
        q = Auth(self.access_key, self.secret_key)
        # 上传到七牛之后保存的文件名
        key = file_path.split('/')[-1]
        # 生成上传 Token，可以指定过期时间等
        token = q.upload_token(self.bucket_name, key, 300)

        ret, info = put_file(token, key, file_path)
        # print(ret)
        # print(info)

    def rename_static_file_in_cdn(self):
        exclude_files = [
            r'.DS_Store',
        ]
        cdn_file_path = configs.Config.CDN_STATIC_ROOT
        file_list = {}
        for x in os.listdir(cdn_file_path):
            if x in exclude_files:
                continue
            file_list[x] = x.replace(Command.SLASH_SUBSTITUTE_BY, '/')

        q = Auth(self.access_key, self.secret_key)
        bucket = BucketManager(q)

        # force为true时强制同名覆盖, 字典的键为原文件，值为目标文件
        ops = build_batch_rename(self.bucket_name, file_list, force='true')
        ret, info = bucket.batch(ops)
        print(ret)
        print(info)
