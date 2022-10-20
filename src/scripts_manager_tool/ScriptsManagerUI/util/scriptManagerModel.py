# coding=utf-8
import json
import os

from PySide2.QtCore import QDir, QFileInfo
from maya import cmds

from peewee import SqliteDatabase, Model, CharField, IntegerField, ManyToManyField, ForeignKeyField, DeferredThroughModel
from scripts_manager_tool import resource

reload(resource)

config_path = resource.getResourcePath().joinpath("config.json").as_posix()
db_path = resource.getResourcePath().joinpath("scripts.db").as_posix()
scripts_path = resource.getResourcePath().parent.parent.parent.joinpath("user_tools").as_posix()

database = SqliteDatabase(db_path)


class BaseModel(Model):
    class Meta:
        database = database


class ScriptType:
    mel_type = 0
    python_script_type = 1
    python_module_type = 2


scripts_collection_deferred = DeferredThroughModel()
glad_scripts_deferred = DeferredThroughModel()


class Script(BaseModel):
    """
    脚本
    """
    name = CharField(unique=True, primary_key=True)
    
    script_type = IntegerField()
    script_path = CharField()
    
    # 如果是python 模块的话 我们还需要一个 module的path 当运行此脚本的时候 把module path添加到系统path里
    script_module_path = CharField()


class ScriptsCollection(BaseModel):
    """
    脚本的集合 也就是当前脚本属于那个类别 一个脚本可以被添加进入多个类别
    """
    
    name = CharField(unique=True, primary_key=True)
    scripts = ManyToManyField(Script, backref="scriptsCollection", through_model=scripts_collection_deferred)


class GladScripts(BaseModel):
    """
    脚本收藏夹 一个用户用一个收藏夹
    """
    user_name = CharField(unique=True, primary_key=True)
    scripts = ManyToManyField(Script, backref="gladScripts", through_model=glad_scripts_deferred)


class ScriptsCollectionThoughModel(BaseModel):
    script = ForeignKeyField(Script)
    scripts_collection = ForeignKeyField(ScriptsCollection)


class GladScriptsThoughModel(BaseModel):
    script = ForeignKeyField(Script)
    glad_scripts = ForeignKeyField(GladScripts)


scripts_collection_deferred.set_model(ScriptsCollectionThoughModel)
glad_scripts_deferred.set_model(GladScriptsThoughModel)


class SqliteHelper:
    def __init__(self):
        self.root_dir = QDir(scripts_path)
        self.config_info = json.loads(open(config_path, "r").read())
        
        with database:
            database.create_tables(
                [
                    Script,
                    ScriptsCollection,
                    GladScripts,
                    ScriptsCollectionThoughModel,
                    GladScriptsThoughModel,
                ], safe=True
            )
    
    def updateScripts(self):
        """
        注意 此项只有特定用户才可以执行
        @return:
        """
        # 先更新数据
        for child in self.root_dir.entryInfoList(QDir.NoSymLinks | QDir.NoDotAndDotDot | QDir.Files | QDir.Dirs):  # type: QFileInfo
            if child.isDir():
                self.__addPythonModule(child)
            elif child.isFile():
                if child.completeSuffix() == "py":
                    self.__addScript(child, typ=ScriptType.python_script_type)
                elif child.completeSuffix() == "mel":
                    self.__addScript(child, typ=ScriptType.mel_type)
        
        # 然后删除从已经从本地磁盘中移除的脚本
        for script in Script.select():
            script_path = script.script_path
            # 若文件已经从硬盘中删除 那么我们需要删除此脚本的信息 且在关联的表格里也要删除此信息
            if not os.path.exists(script_path):
                deleted_script = Script.get(Script.name == script.name)
                deleted_script.delete_instance(recursive=True, delete_nullable=True)
                deleted_script.save()
    
    def addCollection(self, collection_name):
        ScriptsCollection.insert(name=collection_name).on_conflict_ignore().execute()
    
    def addUser(self, user_name):
        GladScripts.insert(user_name=user_name).on_conflict_ignore().execute()
    
    def addScriptToCollection(self, collection_name, script_name):
        """
        将脚本添加到某个类别中
        @param collection_name: 要添加的类别的名字
        @param script_name: 脚本的名字
        @return:
        """
        with database:
            script = Script.get(Script.name == script_name)
            if not script:
                cmds.error(script_name, "is not exists")
                return
            current_collection = ScriptsCollection.get_or_none(ScriptsCollection.name == collection_name)
            
            if current_collection is None:
                cmds.error(collection_name, "is not exists")
                return
            
            if script not in current_collection.scripts:
                current_collection.scripts.add(script)
    
    def removeScriptFromCollection(self, collection_name, script_name):
        with database:
            script = Script.get(Script.name == script_name)
            if not script:
                cmds.error(script_name, "is not exists")
                return
            current_collection = ScriptsCollection.get_or_none(ScriptsCollection.name == collection_name)
            
            if current_collection is None:
                cmds.error(collection_name, "is not exists")
                return
            if script in current_collection.scripts:
                current_collection.scripts.remove(script)
    
    def addScriptToUserGlad(self, user_name, script_name):
        """
        将脚本添加到当前用户的收藏夹中
        @param user_name:
        @param script_name:
        @return:
        """
        with database:
            script = Script.get(Script.name == script_name)
            if not script:
                cmds.error(script_name, "is not exists")
                return
            current_user = GladScripts.get_or_none(GladScripts.user_name == user_name)
            
            if script not in current_user.scripts:
                current_user.scripts.add(script)
    
    def removeScriptFromUserFavor(self, user_name, script_name):
        with database:
            script = Script.get(Script.name == script_name)
            if not script:
                cmds.error(script_name, "is not exists")
                return
            current_user = GladScripts.get_or_none(GladScripts.user_name == user_name)
            
            if current_user is None:
                cmds.error(current_user, "is not exists")
                return
            if script in current_user.scripts:
                current_user.scripts.remove(script)
    
    def __addPythonModule(self, file_info):
        this_dir = QDir(file_info.absoluteFilePath())
        child_files = this_dir.entryInfoList(QDir.NoSymLinks | QDir.NoDotAndDotDot | QDir.Files | QDir.Dirs)
        if len(child_files) != 2 and "scripts" not in [x.fileName() for x in child_files]:
            cmds.error("{} is not a valid script folder".format(file_info.absoluteFilePath()))
            return
        script_info = [p for p in child_files if p.isFile() and p.completeSuffix() == "py"]
        if not script_info:
            cmds.error("not has a scripts to startup {folder}".format(folder=file_info.absoluteFilePath()))
            return
        
        # 在插入之前 我们需要判断 是否有此信息
        module_name = file_info.baseName()
        with database:
            Script.insert(
                name=module_name,
                script_path=script_info[0].absoluteFilePath(),
                script_module_path=file_info.absoluteFilePath(),
                script_type=ScriptType.python_module_type
            ).on_conflict_replace().execute()
    
    def __addScript(self, file_info, typ):
        script_name = file_info.baseName()
        with database:
            Script.insert(
                name=script_name,
                script_path=file_info.absoluteFilePath(),
                script_module_path="",
                script_type=typ
            ).on_conflict_replace().execute()
    
    def getScriptsCollections(self):
        """
        获得当前数据库里所有的集合
        @return:
        """
        return ScriptsCollection.select()
