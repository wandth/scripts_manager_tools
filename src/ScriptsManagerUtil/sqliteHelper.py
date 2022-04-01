import json
import os
import sqlite3
from maya import cmds
from contextlib import closing


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
        for default_tag in self.default_tags.keys() :
            if not os.path.exists(os.path.join(self.scripts_path, default_tag)) :
                continue
            for script in os.listdir(os.path.join(self.scripts_path, default_tag)) :
                script_path = os.path.join(self.scripts_path, default_tag, script).replace("\\", "/")
                if os.path.isdir(script_path) :
                    if (len(os.listdir(script_path)) != 2) and "scripts" not in os.listdir(script_path) :
                        cmds.error("{} is not a valid script folder".format(script_path))
                    script_name = filter(lambda x : x.endswith(".py"), os.listdir(script_path))[0]

                    self.__updateScript(name = os.path.splitext(script_name)[0],
                                        script_path = os.path.join(script_path, script_name).replace("\\", "/"),
                                        script_type = "python", python_type = "module", tag = default_tag)
                elif os.path.isfile(script_path) :
                    if script_path.endswith(".py") :
                        self.__updateScript(name = os.path.splitext(script)[0], script_path = script_path, script_type = "python", python_type = "script", tag = default_tag)
                    elif script_path.endswith(".mel") :
                        self.__updateScript(name = os.path.splitext(script)[0], script_path = script_path, script_type = "mel", python_type = "", tag = default_tag)

        for current_file in os.listdir(self.scripts_path) :
            script_path = os.path.join(self.scripts_path, current_file).replace("\\", "/")
            if os.path.isdir(script_path) :
                continue
            if script_path.endswith(".py") :
                self.__updateScript(name = os.path.splitext(current_file)[0], script_path = script_path, script_type = "python", python_type = "script", tag = "")
            if script_path.endswith(".mel") :
                self.__updateScript(name = os.path.splitext(current_file)[0], script_path = script_path, script_type = "mel", python_type = "", tag = "")

    def __updateScript(self, name, script_path, script_type, python_type, tag) :
        with closing(sqlite3.connect(self.db_path)) as database :
            database.text_factory = bytes
            cursor = database.cursor()

            cursor.execute("""SELECT * FROM scripts WHERE name = "{name}" """.format(name = getStr(name)))
            if cursor.fetchall() :
                update_str = """UPDATE scripts SET script_path = "{script_path}", type = "{script_type}", python_type = "{python_type}" WHERE name = "{name}" """.format(
                    script_path = getStr(script_path), script_type = script_type, python_type = python_type, name = getStr(name))
                cursor.execute(update_str)
            else :
                insert_str = """INSERT INTO scripts(name, script_path, type, python_type) VALUES("{name}", "{script_path}", "{script_type}", "{python_type}")""".format(
                    name = getStr(name), script_path = getStr(script_path), script_type = script_type, python_type = python_type)
                cursor.execute(insert_str)

            database.commit()

        if tag != "" :
            self.addScriptTag(script_name = name, tag_name = tag)


    def addScriptTag(self, script_name, tag_name) :
        with closing(sqlite3.connect(self.db_path)) as database :
            database.text_factory = bytes
            cursor = database.cursor()

            cursor.execute("""SELECT * FROM scripts_tags WHERE script_name = "{script_name}" AND tag_name = "{tag_name}" """.format(
                script_name = getStr(script_name), tag_name = tag_name))
            if not cursor.fetchall() :
                insert_str = """INSERT INTO scripts_tags(script_name, tag_name) VALUES("{script_name}", "{tag_name}")""".format(
                    script_name = getStr(script_name), tag_name = tag_name)
                cursor.execute(insert_str)
            database.commit()

    def deleteScriptTag(self, script_name, tag_name) :
        pass

    def deleteTag(self, tag_name) :
        pass

    def addTag(self, tag_name) :
        pass


def getStr(chinese_str) :
    try :
        return chinese_str.encode("gb2312")
    except :
        return chinese_str.decode("gbk").encode("gb2312")
