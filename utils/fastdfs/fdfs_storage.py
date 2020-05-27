# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.files.storage import Storage


class FdfsStorage(Storage):

    def __init__(self, base_url=None):
        self.base_url = base_url or settings.FDFS_BASE_URL

    def _open(self,name, mode='rb'):
        pass

    def _save(self,name, content):
        pass

    def url(self, name):
        return self.base_url + name
