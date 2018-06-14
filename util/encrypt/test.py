# coding:utf-8

import time
import sys


total = 100
for i in range(1,101):
    print "\r已完成{}%【{}】".format(i*100/total,"*"*(i*50/total)),
    # print(i,end="")
    # sys.stdout.flush()
    time.sleep(0.1)