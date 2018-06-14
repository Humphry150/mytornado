# coding:utf-8

from handlers import image, image2, default

urlpatterns = [
    (r'/', default.DefaultHandler, ),
    (r'/image/', image.ImageDecryptHandler,),
]  