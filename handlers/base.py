# coding:utf-8


import tornado.web
import logging
logging.basicConfig()
logging.debug()

class BaseRequestHandler(tornado.web.RequestHandler):

    def get(self, *args, **kwargs):
        pass

    def post(self, *args, **kwargs):
        pass

    def head(self, *args, **kwargs):
        pass

    def delete(self, *args, **kwargs):
        pass

    def patch(self, *args, **kwargs):
        pass

    def put(self, *args, **kwargs):
        pass

    def options(self, *args, **kwargs):
        pass
