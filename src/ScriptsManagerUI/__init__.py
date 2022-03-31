# -*- coding:utf-8 -*-
import maya.cmds as cm
import maya.OpenMayaUI as omui
import maya.api.OpenMaya as om
import maya.mel as mel
import os
import getpass
import sys
import json
import traceback
from collections import OrderedDict
from collections import deque
import sqlite3
import thread
import time
import toolbox_library.windows.toolbox_class.scriptFileHelp as scriptFileHelp

try :
    from PySide.QtCore import *
    from PySide.QtGui import *
    from PySide import __version__
    from shiboken import wrapInstance
except :
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
    from PySide2 import __version__
    from shiboken2 import wrapInstance

'''
lock = thread.allocate_lock()
def syncEvalFileData(threadId,databaseFilePath):
    lock.acquire()
    print('%s in'%threadId)
    time.sleep(3)
    lock.release()
    thread.exit_thread()
'''


def sqlQueryExcute(databasePath, sqlStatement, sqlStatementArgs = tuple()) :
    u'''
    sqlQueryExcute
    用于查询

    databasePath (str) : 数据库文件路径
    sqlStatement (str) : sqlite语句
    sqlStatementArgs (tuple) : sqlite语句的参数
    return : 查询到的结果
    '''
    conn = sqlite3.connect(databasePath)

    cursor = conn.cursor()
    cursor.execute(sqlStatement, sqlStatementArgs)
    values = cursor.fetchall()

    cursor.close()
    conn.commit()
    conn.close()
    return values


def sqlExcute(databasePath, sqlStatements) :
    u'''
    sqlExcute
    用于执行除查询外的多条语句

    databasePath (str) : 数据库文件路径
    sqlStatement (list) : sqlite语句
    '''
    conn = sqlite3.connect(databasePath)

    cursor = conn.cursor()
    for sqlStatement in sqlStatements :
        cursor.execute(sqlStatement)

    cursor.close()
    conn.commit()
    conn.close()


class PublicServerDatabase(object) :
    u'''
    公有数据库服务器端

    用于创建及更新插件库
    '''

    def __init__(self, databasePath, depositoriePath) :
        super(PublicServerDatabase, self).__init__()
        self.databasePath = databasePath
        self.depositoriePath = depositoriePath

    def updateTables(self) :
        # 如果没有表就创建表
        # table script
        sqlStatement = u'''
            SELECT COUNT(*) FROM sqlite_master where type='table' and name='script'
        '''
        if not sqlQueryExcute(self.databasePath, sqlStatement)[0][0] :

            sqlExcute(self.databasePath, [u'''create table script(
                id INTEGER primary key AUTOINCREMENT not null,
                basename text not null UNIQUE,
                filepath text not null)
            '''])

        # table label
        sqlStatement = u'''
            SELECT COUNT(*) FROM sqlite_master where type='table' and name='label'
        '''
        if not sqlQueryExcute(self.databasePath, sqlStatement)[0][0] :

            sqlExcute(self.databasePath, [u'''create table label(
                id INTEGER primary key AUTOINCREMENT not null,
                labelname text not null UNIQUE,
                label_type_id int not null)
            '''])

        # table label_record
        sqlStatement = u'''
            SELECT COUNT(*) FROM sqlite_master where type='table' and name='label_record'
        '''
        if not sqlQueryExcute(self.databasePath, sqlStatement)[0][0] :

            sqlExcute(self.databasePath, [u'''create table label_record(
                id INTEGER primary key AUTOINCREMENT not null,
                script_id int not null,
                label_id int not null)
            '''])

        # table label_type
        sqlStatement = u'''
            SELECT COUNT(*) FROM sqlite_master where type='table' and name='label_type'
        '''
        if not sqlQueryExcute(self.databasePath, sqlStatement)[0][0] :

            sqlExcute(self.databasePath, [u'''create table label_type(
                id INTEGER primary key AUTOINCREMENT not null,
                type text not null UNIQUE)
            '''])

            sqlExcute(self.databasePath, [u'''
                insert into label_type (type) values (\'official\')''',
                                          '''insert into label_type (type) values (\'personal\')'''])

    def updateRecords(self) :

        # 根据一个evalFileList得到另一个带名字和目录的list
        time1 = time.time()

        evalFileList = scriptFileHelp.getEvalFileList(unicode(self.depositoriePath))
        nameAndPathList = list()
        basenameList = list()
        # basenameList的小写版本，对比用
        basenameLowerList = list()
        for evalFile in evalFileList :
            basename = os.path.basename(evalFile)
            ext = os.path.splitext(basename)[1].lower()
            basename = basename[:-len(ext)]
            basenameList.append(basename)
            basenameLowerList.append(basename.lower())
            nameAndPathList.append((basename, evalFile))

        time2 = time.time()

        conn = sqlite3.connect(self.databasePath)
        cursor = conn.cursor()

        sqlStatement = u'''select * from script'''
        cursor.execute(sqlStatement)
        values = cursor.fetchall()
        for i in range(len(values)) :
            scriptInfo = values[i]
            # 有没有这个script
            # 有的话filepath对不对
            # 没有就删掉
            if scriptInfo[1].lower() in basenameLowerList :
                index = basenameLowerList.index(scriptInfo[1].lower())

                sqlStatement = u'''select filepath from script where basename=\'%s\' COLLATE NOCASE''' % scriptInfo[1]
                cursor.execute(sqlStatement)
                filepaths = cursor.fetchall()
                changeText = ''
                if filepaths[0][0] != nameAndPathList[index][1] :
                    cursor.execute(u'''
                            update script set filepath = \'%s\' where basename = \'%s\'
                        ''' % (nameAndPathList[index][1], scriptInfo[1]))
                    changeText = u'更改 %s' % scriptInfo[1]

                if scriptInfo[1] != basenameList[index] :
                    cursor.execute(u'''
                            update script set basename = \'%s\' where basename = \'%s\'
                        ''' % (basenameList[index], scriptInfo[1]))
                    changeText = u'更改 %s' % scriptInfo[1]

                if changeText :
                    print(changeText)

                del basenameList[index]
                del basenameLowerList[index]
                del nameAndPathList[index]
                # 处理完删掉basenameList里面和nameAndPathList里面的元素
            else :
                sqlStatement = u'''
                delete from label_record where script_id = (select id from script where basename = \'%s\')
                ''' % scriptInfo[1]
                cursor.execute(sqlStatement)

                sqlStatement = u'''
                delete from script where basename = \'%s\'
                ''' % scriptInfo[1]
                cursor.execute(sqlStatement)

                print(u'删掉 %s' % scriptInfo[1])

        # 如果basenameList还有元素，判断是否在数据库有script，没有就加进去
        if nameAndPathList :
            for nameAndPath in nameAndPathList :
                basename, path = nameAndPath
                sqlStatement = u'''select * from script where basename=\'%s\' COLLATE NOCASE''' % basename
                cursor.execute(sqlStatement)
                values = cursor.fetchall()
                if values == list() or not values[0][0] :
                    cursor.execute(u'''
                            insert into script (basename, filepath) values (\'%s\',\'%s\')
                        ''' % (basename, path))

                    print(u'添加 %s' % basename)

        cursor.close()
        conn.commit()
        conn.close()

        time3 = time.time()
        print(time2 - time1)
        print(time3 - time2)


class PublicCustomerDatabase(object) :
    u'''
    公有数据库客户端

    用于添加标签
    '''

    def __init__(self, databasePath) :
        super(PublicCustomerDatabase, self).__init__()
        self.databasePath = databasePath

    def getScriptPathFromScriptName(self, name) :
        values = sqlQueryExcute(self.databasePath, u'''
            select filepath from script where basename=\'%s\' COLLATE NOCASE
        ''' % name)
        if values != list() :
            return values[0][0]
        else :
            return None

    def getScriptPathListFromScriptNameList(self, nameList) :
        pathList = list()
        if nameList :
            conn = sqlite3.connect(self.databasePath)
            cursor = conn.cursor()

            for name in nameList :
                sqlStatement = u'''
                    select filepath from script where basename=\'%s\' COLLATE NOCASE
                ''' % name
                cursor.execute(sqlStatement)
                values = cursor.fetchall()
                pathList.append(values[0][0])

            cursor.close()
            conn.commit()
            conn.close()

        return pathList

    def getNamesFromExpression(self, strList) :
        u'''
        通过字符串表达式来搜索得出脚本列表
        '''
        conn = sqlite3.connect(self.databasePath)
        cursor = conn.cursor()

        sqlStatement = u''''''

        # sqlStatement = u'''select basename from script where '''
        for i in range(len(strList)) :
            str = strList[i]
            baseStatement = u'''
            select basename from (select basename from script where id in 
            (select script_id from label_record where label_id in 
            (select id from label where labelname like \'%%%s%%\')) union 
            select basename from script where basename like \'%%%s%%\')
            ''' % (str, str)
            if not i :
                sqlStatement += baseStatement
            else :
                sqlStatement += (u''' intersect ''' + baseStatement)

        cursor.execute(sqlStatement)
        values = cursor.fetchall()

        cursor.close()
        conn.commit()
        conn.close()

        nameList = list()
        if values != list() :
            for value in values :
                nameList.append(value[0])
        return nameList

    def addLabel(self, label, label_type_id) :
        conn = sqlite3.connect(self.databasePath)
        cursor = conn.cursor()

        # 没有这个label，需要添加进label表
        cursor.execute(u'''select * from label where labelname = \'%s\' COLLATE NOCASE''' % label)
        values = cursor.fetchall()
        if values == list() or not values[0][0] :
            cursor.execute(u'''insert into label (labelname,label_type_id) values (\'%s\',%d)''' % (label, label_type_id))

        cursor.close()
        conn.commit()
        conn.close()

    def addLabelToName(self, name, label, label_type_id = 2) :
        '''
        return:
            True 添加成功/本来已存在
            False 没有这个name的script所以添加失败
        '''
        conn = sqlite3.connect(self.databasePath)
        cursor = conn.cursor()

        # 如果script已经被删除，无需添加label
        sqlStatement = u'''select * from script where basename=\'%s\' COLLATE NOCASE''' % name
        cursor.execute(sqlStatement)
        values = cursor.fetchall()
        if values != list() and values[0][0] :

            hasName = True

            # 没有这个label，需要添加进label表
            cursor.execute(u'''select * from label where labelname = \'%s\' COLLATE NOCASE''' % label)
            values = cursor.fetchall()
            if values == list() or not values[0][0] :
                cursor.execute(u'''insert into label (labelname,label_type_id) values (\'%s\',%d)''' % (label, label_type_id))

            # 关联
            cursor.execute(u'''select * from label_record where script_id = (
                select id from script where basename = \'%s\' COLLATE NOCASE) and label_id = (
                select id from label where labelname = \'%s\' COLLATE NOCASE)''' % (name, label))
            values = cursor.fetchall()
            if values == list() or not values[0][0] :
                cursor.execute(u'''
                    insert into label_record (script_id,label_id) values (
                        (select id from script where basename = \'%s\' COLLATE NOCASE),
                        (select id from label where labelname = \'%s\' COLLATE NOCASE)
                    )
                ''' % (name, label))
        else :
            hasName = False

        cursor.close()
        conn.commit()
        conn.close()

        return hasName

    def removeLabel(self, name, label) :
        '''
        return:
            True 移除成功/本来就没关联
            False 没有这个name的script所以移除失败
                  没有这个label也会移除失败
        '''
        conn = sqlite3.connect(self.databasePath)
        cursor = conn.cursor()

        # 如果script已经被删除，无需移除label
        sqlStatement = u'''select * from script where basename=\'%s\' COLLATE NOCASE''' % name
        cursor.execute(sqlStatement)
        values = cursor.fetchall()
        if values != list() and values[0][0] :
            # 没有这个label，不需移除
            cursor.execute(u'''select * from label where labelname = \'%s\' COLLATE NOCASE''' % label)
            values = cursor.fetchall()
            if values == list() or not values[0][0] :
                isRemove = False
            else :
                # 关联
                sqlStatement = u'''select * from label_record where script_id = (
                    select id from script where basename = \'%s\' COLLATE NOCASE) and label_id = (
                    select id from label where labelname = \'%s\' COLLATE NOCASE)''' % (name, label)
                cursor.execute(sqlStatement)
                values = cursor.fetchall()
                if values != list() and values[0][0] :
                    cursor.execute(u'''
                        delete from label_record where script_id = (
                            select id from script where basename = \'%s\' COLLATE NOCASE) and label_id = (
                            select id from label where labelname = \'%s\' COLLATE NOCASE)
                    ''' % (name, label))
                isRemove = True
        else :
            isRemove = False

        cursor.close()
        conn.commit()
        conn.close()

        return isRemove

    def deleteLabels(self, labels) :
        u'''
        输入一个标签列表，对每个标签：
        删除label表里面的这个标签，并且删除label_record表里面这个标签的关联记录
        '''

        conn = sqlite3.connect(self.databasePath)

        cursor = conn.cursor()

        for label in labels :
            sqlStatements = ["delete from label_record where label_id = (select id from label where labelname = '%s')" % label,
                             "delete from label where labelname = '%s'" % label]
            for sqlStatement in sqlStatements :
                cursor.execute(sqlStatement)
            print(u'删除标签 %s' % label)

        cursor.close()
        conn.commit()
        conn.close()

    def getAllScriptNamesAndPaths(self) :
        scriptNamesAndPaths = list()

        conn = sqlite3.connect(self.databasePath)
        cursor = conn.cursor()

        sqlStatement = u'''select basename from script'''
        cursor.execute(sqlStatement)
        values = cursor.fetchall()

        if values != list() :
            for value in values :
                scriptNamesAndPaths.append({'name' : value[0]})

            sqlStatement = u'''select filepath from script'''
            cursor.execute(sqlStatement)
            values = cursor.fetchall()

            for i in range(len(values)) :
                scriptNamesAndPaths[i]['path'] = values[i][0]

        cursor.close()
        conn.commit()
        conn.close()

        return scriptNamesAndPaths

    def getAllLabels(self) :
        allLabels = list()

        conn = sqlite3.connect(self.databasePath)
        cursor = conn.cursor()

        sqlStatement = u'''select labelname from label'''
        cursor.execute(sqlStatement)
        values = cursor.fetchall()

        if values != list() :
            for value in values :
                allLabels.append(value[0])
        cursor.close()
        conn.commit()
        conn.close()

        return allLabels

    def getLabelsFromTyps(self, type_id) :
        labels = list()

        conn = sqlite3.connect(self.databasePath)
        cursor = conn.cursor()

        sqlStatement = u'''select labelname from label where label_type_id = %d''' % type_id
        cursor.execute(sqlStatement)
        values = cursor.fetchall()

        if values != list() :
            for value in values :
                labels.append(value[0])
        cursor.close()
        conn.commit()
        conn.close()

        return labels

    def getAllLabelsAndTyps(self) :
        allLabelsAndTypes = list()

        conn = sqlite3.connect(self.databasePath)
        cursor = conn.cursor()

        sqlStatement = u'''select labelname,label_type_id from label'''
        cursor.execute(sqlStatement)
        values = cursor.fetchall()

        if values != list() :
            for value in values :
                allLabelsAndTypes.append({'label' : value[0], 'type_id' : value[1]})
        cursor.close()
        conn.commit()
        conn.close()

        return allLabelsAndTypes

    def getLabelsFromScript(self, scriptName) :
        allLabels = list()

        conn = sqlite3.connect(self.databasePath)
        cursor = conn.cursor()

        sqlStatement = u'''
            select label_id from label_record where script_id = 
            (select id from script where basename = \'%s\' COLLATE NOCASE)
        ''' % scriptName
        cursor.execute(sqlStatement)
        values = cursor.fetchall()

        if values != list() :
            for value in values :

                sqlStatement = u'''
                    select labelname from label where id = %d
                ''' % value
                cursor.execute(sqlStatement)
                las = cursor.fetchall()

                allLabels.append(las[0][0])
        cursor.close()
        conn.commit()
        conn.close()

        return allLabels

    def getTypeFromLabel(self, label) :
        type = -1

        conn = sqlite3.connect(self.databasePath)
        cursor = conn.cursor()

        sqlStatement = u'''select label_type_id from label where labelname = \'%s\'''' % label
        cursor.execute(sqlStatement)
        values = cursor.fetchall()

        if values != list() :
            type = values[0][0]
        cursor.close()
        conn.commit()
        conn.close()

        return type

    def getLabelsAndTypesFromScript(self, scriptName) :
        allLabels = list()

        conn = sqlite3.connect(self.databasePath)
        cursor = conn.cursor()

        sqlStatement = u'''
            select label_id from label_record where script_id = 
            (select id from script where basename = \'%s\' COLLATE NOCASE)
        ''' % scriptName
        cursor.execute(sqlStatement)
        values = cursor.fetchall()

        if values != list() :
            for value in values :

                sqlStatement = u'''
                    select labelname,label_type_id from label where id = %d
                ''' % value
                cursor.execute(sqlStatement)
                las = cursor.fetchall()

                allLabels.append({'name' : las[0][0], 'type_id' : las[0][1]})
        cursor.close()
        conn.commit()
        conn.close()

        return allLabels

    def getLabelsAndCountsFromTyps(self, type) :
        u'''
        从一个标签类型得到标签列表，
        和每个标签的记录数量列表（即标签有多少工具使用）。
        '''
        labels = list()

        conn = sqlite3.connect(self.databasePath)
        cursor = conn.cursor()

        sqlStatement = u'''select labelname from label where label_type_id = %d''' % type
        cursor.execute(sqlStatement)
        values = cursor.fetchall()

        if values != list() :
            for value in values :
                labels.append(value[0])

        countList = list()
        for label in labels :
            sqlStatement = u'''
                select COUNT(*) from label_record where label_id = (select id from label where labelname = "%s")
            ''' % label
            cursor.execute(sqlStatement)
            values = cursor.fetchall()
            try :
                countList.append(values[0][0])
            except :
                countList.append(0)

        cursor.close()
        conn.commit()
        conn.close()

        return (labels, countList)

    def isOfficialLabel(self, label) :
        u'''
        label是否官方标签？
        '''
        conn = sqlite3.connect(self.databasePath)
        cursor = conn.cursor()

        sqlStatement = u'''select COUNT(id) from label where label_type_id = 
        (select id from label_type where type = \'official\') and labelname = 
        \'%s\' COLLATE NOCASE''' % label
        cursor.execute(sqlStatement)
        values = cursor.fetchall()

        isOfficialLabel = False
        if values != list() :
            # print(values)
            if values[0][0] != 0 :
                isOfficialLabel = True
        cursor.close()
        conn.commit()
        conn.close()
        return isOfficialLabel


# create table label(id int primary key not null,labelname text not null UNIQUE)
# select * from script where basename='ABC动画传递'
# select filepath from script where basename='ABC动画传递'
# update script set filepath = 'a' where basename = 'ABC动画传递'
# select label_id from label_record where script_id = (select id from script where basename = 'ABC动画传递')


def PublicServerDatabaseReady(databaseFile, depositoriePath) :
    u'''
    创建或更新服务器数据的快捷函数
    '''
    serverDatabase = PublicServerDatabase(databaseFile, depositoriePath)
    serverDatabase.updateTables()
    serverDatabase.updateRecords()

