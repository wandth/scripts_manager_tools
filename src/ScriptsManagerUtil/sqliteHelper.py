# coding=utf-8
import json
import sqlite3
from maya import cmds
from contextlib import closing
from PySide2.QtCore import QDir, QFileInfo


class SqliteHelper :
    def __init__(self, db_path = "E:/python/scripts_manager_tools/src/resource/scripts.db",
                 scripts_path = "E:/python/scripts_manager_tools/user_tools",
                 config_path = "E:/python/scripts_manager_tools/src/resource/config.json"
                 ) :
        self.db_path = db_path
        self.scripts_path = scripts_path
        self.config_info = json.loads(open(config_path, "r").read())
        self.default_tags = self.config_info["default_tags"]

        self.createTable()

    def createTable(self) :
        database = sqlite3.connect(self.db_path)
        cursor = database.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scripts(
                name TEXT NOT NULL PRIMARY KEY,
                script_path TEXT NOT NULL,
                type TEXT NOT NULL,
                python_type TEXT NOT NULL)""")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tags(
                name TEXT NOT NULL PRIMARY KEY,
                can_be_delete INTEGER NOT NULL)""")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scripts_tags(
                script_name TEXT NOT NULL,
                tag_name TEXT NOT NULL)""")

        for tag in self.default_tags.keys() :
            cursor.execute("""INSERT INTO tags(name, can_be_delete) select ?, ? where not exists(select * from tags where name = ?)""",
                           (tag, 1, tag))
        database.commit()
        database.close()

    def updateScriptsTable(self) :
        root_dir = QDir(self.scripts_path)
        for root_child in root_dir.entryInfoList(QDir.NoSymLinks | QDir.NoDotAndDotDot | QDir.Files | QDir.Dirs) :  # type: QFileInfo
            # 遍历全部的根组的子文件夹
            if root_child.isDir() and root_child.baseName() in self.default_tags.keys() :
                for child in QDir(root_child.absoluteFilePath()).entryInfoList(QDir.NoSymLinks | QDir.NoDotAndDotDot | QDir.Files | QDir.Dirs) :  # type: QFileInfo
                    if child.isDir() :
                        self.__updateFolder(child, tag = root_child.baseName())
                    elif child.isFile() :
                        self.__updateFile(child, tag = root_child.baseName())
            elif root_child.isDir() and root_child.baseName() not in self.default_tags.keys() :
                self.__updateFolder(root_child, tag = "")
            if root_child.isFile() :
                self.__updateFile(root_child, tag = "")

    def addScriptTag(self, script_name, tag_name) :
        with closing(sqlite3.connect(self.db_path)) as database :
            database.text_factory = bytes
            cursor = database.cursor()

            cursor.execute(U"""SELECT * FROM scripts_tags WHERE script_name = "{script_name}" AND tag_name = "{tag_name}" """.format(
                script_name = script_name, tag_name = tag_name))
            if not cursor.fetchall() :
                insert_str = U"""INSERT INTO scripts_tags(script_name, tag_name) VALUES("{script_name}", "{tag_name}")""".format(
                    script_name = script_name, tag_name = tag_name)

                cursor.execute(insert_str)
            database.commit()

    def deleteScriptTag(self, script_name, tag_name) :
        pass

    def deleteTag(self, tag_name) :
        pass

    def addTag(self, tag_name) :
        pass

    def __updateFolder(self, file_ino, tag) :
        new_folder = QDir(file_ino.absoluteFilePath())
        child_files = new_folder.entryInfoList(QDir.NoSymLinks | QDir.NoDotAndDotDot | QDir.Files | QDir.Dirs)
        if len(child_files) != 2 and "scripts" not in [x.fileName() for x in child_files] :
            cmds.error("{} is not a valid script folder".format(file_ino.absoluteFilePath()))
            return
        script_infos = [p for p in child_files if p.isFile() and p.completeSuffix() == "py"]
        if not script_infos :
            cmds.error("not has a scripts to startup {folder}".format(folder = new_folder.absoluteFilePath()))
            return
        self.__updateScript(name = script_infos[0].baseName(),
                            script_path = script_infos[0].absoluteFilePath(),
                            script_type = "python", python_type = "module", tag = tag)

    def __updateFile(self, file_ino, tag) :
        if file_ino.completeSuffix() == "py" :
            self.__updateScript(name = file_ino.baseName(), script_path = file_ino.absoluteFilePath(), script_type = "python", python_type = "script", tag = tag)
        elif file_ino.completeSuffix() == "mel" :
            self.__updateScript(name = file_ino.baseName(), script_path = file_ino.absoluteFilePath(), script_type = "mel", python_type = "", tag = tag)

    def __updateScript(self, name, script_path, script_type, python_type, tag) :
        with closing(sqlite3.connect(self.db_path)) as database :
            database.text_factory = bytes
            cursor = database.cursor()

            cursor.execute(U"""SELECT * FROM scripts WHERE name = "{name}" """.format(name = name))
            if cursor.fetchall() :
                update_str = U"""UPDATE scripts SET script_path = "{script_path}", type = "{script_type}", python_type = "{python_type}" WHERE name = "{name}" """.format(
                    script_path = script_path, script_type = script_type, python_type = python_type, name = name)
                cursor.execute(update_str)
            else :
                insert_str = U"""INSERT INTO scripts(name, script_path, type, python_type) VALUES("{name}", "{script_path}", "{script_type}", "{python_type}")""".format(
                    name = name, script_path = script_path, script_type = script_type, python_type = python_type)
                cursor.execute(insert_str)
            database.commit()

        if tag != "" :
            self.addScriptTag(script_name = name, tag_name = tag)
