# coding:utf-8

import os
from handlers.base import BaseRequestHandler
from util.encrypt import decrypt


class ImageDecryptHandler(BaseRequestHandler):

    def get(self, *args, **kwargs):
        full_name = "/data/test/static/images/757f09ddfe454e6aff8b726c7497955d.jpg"
        res = decrypt.image_decrypt(full_name)
        self.write(res)
        self.set_header("Content-type", "image/jpg")


