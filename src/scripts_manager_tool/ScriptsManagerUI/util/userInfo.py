# coding=utf-8
import subprocess
from maya import cmds


class UserInfo(object) :
    def __init__(self) :
        self.__setupUserInfo()

    @property
    def userName(self) :
        return self.__user_name

    @property
    def organization(self) :
        return self.__organization

    def __setupUserInfo(self) :
        info = self.__getUserInfo()
        if info :
            info_list = info.split(',')
            self.__user_name = info_list[0][3 :]
            self.__organization = info_list[1][3 :]

    @staticmethod
    def __getUserInfo() :
        if not cmds.about(b = True) :
            pi = subprocess.Popen('WHOAMI /FQDN', shell = True, stdout = subprocess.PIPE)
            info = pi.stdout.read()
            if info :
                info = info.split()[0].decode('GBK')
                return info
            else :
                return None
