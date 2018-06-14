# coding: utf8

import os
import sys
import zlib
import pyinotify
import base64
import logging
from Crypto.Cipher import AES
import shutil


error_tips = u"命令有误，请确保命令类下：\n" \
             u"1、'python directory_encrypt.py dir': 对dir路径下的所有图片进行加密操作\n" \
             u"2、'python directory_encrypt.py dir listen':监听dir路径是否发生变化"


class DirChangeEventHandler(pyinotify.ProcessEvent):
    def my_init(self):
        logging.basicConfig(
            filename="./image_dir_change.log",
            level=logging.INFO,
            format="%(asctime)-15s %(levelname)s %(filename)s %(lineno)d %(process)d %(message)s",
            datefmt="%a %d %b %Y %H:%M:%S",
        )

    def __init__(self, directory):
        super(DirChangeEventHandler, self).__init__()
        self.img_handler = ImageEncryptHandler(directory, True)


    def get_abspath(self, path, name):
        directory = path if path.endswith("/") else "{}/".format(path)
        return directory+name

    def do_image_encrypt(self, directory):
        if os.path.isfile(directory):
            # 是一个文件
            self.img_handler.image_encrypt_compress(directory)
        else:
            # 是一个文件夹
            self.img_handler.directory_encrypt(directory)

    def process_IN_MODIFY(self, event):
        """ 文件被修改时触发
        :param event:
        :return:
        """
        directory = self.get_abspath(event.path, event.name)
        self.do_image_encrypt(directory)


    def process_IN_CREATE(self, event):
        """ 创建文件
        :param event:
        :return:
        """
        directory = self.get_abspath(event.path, event.name)
        self.do_image_encrypt(directory)




class ImageEncryptHandler(object):

    def __init__(self, directory, is_listen=False, key="abcdefghijklmnop"):
        logging.basicConfig(
            filename="./image_encrypt_error.log",
            level=logging.INFO,
            format="%(asctime)-15s %(levelname)s %(filename)s %(lineno)d  %(message)s",
            datefmt="%a %d %b %Y %H:%M:%S",
        )
        self.current_count = 0
        self.all_image_count = 0
        self.directory = directory
        self.image_ext = [".jpg", ".jpeg", ".png", ".bmp", "tiff", "gif", "psd"]
        self.is_listen = is_listen

        # 这里密钥key 长度必须为16（AES-128）、24（AES-192）、或32（AES-256）Bytes 长度.
        # 目前AES-128足够用
        if len(key) < 16:
            key = key + (16 - len(key)) * "\0"
        self.key = key[:16]
        self.mode = AES.MODE_CBC

        # 读取目录文件数目
        self.get_all_image_count(directory)

    # 加密函数，如果text不是16的倍数【加密文本text必须为16的倍数！】，那就补足为16的倍数
    def aes_encrypt(self, text):
        cryptor = AES.new(self.key, self.mode, IV=self.key)
        length = 16
        count = len(text)
        add = count % length
        if add:
            text = text + ('\0' * (length-add))
        self.ciphertext = cryptor.encrypt(text)

        # 因为AES加密时候得到的字符串不一定是ascii字符集的，输出到终端或者保存时候可能存在问题
        # 所以这里统一把加密后的字符串用base64转化
        return base64.b64encode(self.ciphertext)

    def check_image(self, filename):
        """
        检查图片是不是加密文件
        :param filename:
        :return:True:是加密文件；False:不是加密文件
        """
        with open(filename, 'r') as fp:
            content = fp.read()
            if content.startswith("YUNFAN"):
                # 是加密图片
                return True
            else:
                return False

    def get_all_image_count(self, directory):
        """
        获取目录下的所有图片总数
        :param directory: 目录
        """
        directory = directory if directory.endswith("/") else "{}/".format(directory)
        if os.path.exists(directory):
            lists = os.listdir(directory)
            for val in lists:
                if os.path.isfile(directory + val) and (os.path.splitext(val)[1].lower() in self.image_ext):
                    # 如果是图片
                    if not self.check_image(directory + val):
                        # 如果不是加密的图片
                        self.all_image_count += 1
                elif os.path.isdir(directory + val):
                    # 如果是目录
                    self.get_all_image_count(directory + val)

    def image_encrypt_compress(self, current_file):
        """
        对某个文件执行加密和压缩
        :param current_file:
        :return:
        """
        fr, fw = None, None
        try:
            fr = open(current_file, 'rb')
            mark = fr.read(6)

            if not mark.startswith("YUNFAN"):

                fr.seek(0)
                before_text = fr.read()
                fr.close()

                # 当图片未加密时，创建临时文件
                tmp_file = "{}.tmp".format(current_file)
                fw = open(tmp_file, "wb")

                # 对内容进行aes对称加密
                after_text = self.aes_encrypt(before_text)

                # 对内容进行压缩
                after_comp = zlib.compress(after_text)

                # 加密和压缩成功，则写入临时文件：内容开头处添加一个标记，下次执行压缩图片的脚本时就可以跳过这个文件
                fw.write("YUNFAN" + after_comp)

                # 关闭临时文件
                fw.close()

                # 将临时文件拷贝到非临时文件
                shutil.copy(tmp_file, current_file)

                # 如果文件拷贝成功，删除临时文件
                os.remove(tmp_file)

                flag = True
            else:
                flag = False

        except:
            logging.info("raise exception when exec do_ncrypt({})".format(current_file))
            flag = False
        finally:
            # 关闭文件
            if fr is not None and not fr.closed:
                fr.close()
            if fw is not None and not fw.closed:
                fw.close()
            return flag

    def directory_encrypt(self, directory=None):
        """
        对某个目录执行加密
        :param directory:目录
        :return:
        """
        if directory is None:
            directory = self.directory
        # 目录处理
        directory = directory if directory.endswith("/") else "{}/".format(directory)

        if os.path.exists(directory):
            # 目录存在

            # 遍历目录下的所有图片
            for item in os.listdir(directory):
                current_file = directory + item
                ext = os.path.splitext(item)[1]
                if os.path.isfile(current_file) and (ext.lower() in self.image_ext):
                    # 图片
                    # 如果是指定类型的图片文件，则执行加密操作)
                    try:
                        res = self.image_encrypt_compress(current_file)
                        if res:
                            self.current_count += 1
                            # 显示加密进度
                            if not self.is_listen:
                                print "\r已完成{}%".format(self.current_count * 100 / self.all_image_count),
                                sys.stdout.flush()
                    except:
                        logging.info("raise exception when exec self.image_encrypt_compress({})".format(current_file))
                elif os.path.isdir(current_file):
                    # 目录
                    self.directory_encrypt(current_file)
        else:
            # 目录不存在
            logging.info("the directory “{}” is not exist when exec directory_encrypt()\n".format(directory))


if __name__ == "__main__":
    # aes对称加密的密钥，长度最好为16位
    params = sys.argv
    if len(params) == 1:
        # 不带参数
        print(error_tips)
    elif len(params) == 2:
        target_dir = params[1]
        obj = ImageEncryptHandler(target_dir)
        obj.directory_encrypt()
    elif len(params) == 3:
        if params[2].strip().lower() != "listen":
            print(error_tips)
        else:
            target_dir = params[1]

            wm = pyinotify.WatchManager()
            wm.add_watch(target_dir, pyinotify.ALL_EVENTS, rec=True)
            # /tmp是可以自己修改的监控的目录
            # event handler
            eh = DirChangeEventHandler(target_dir)
            # notifier
            notifier = pyinotify.Notifier(wm, eh)
            notifier.loop()
    else:
        print(error_tips)


