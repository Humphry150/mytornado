# coding:utf-8

import tornado.ioloop
import tornado.web

from configs import settings, urls



def main():
    app = tornado.web.Application(urls.urlpatterns, **settings.application_settings)
    app.listen(settings.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
