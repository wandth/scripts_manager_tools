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


scripts_tags_deferred = DeferredThroughModel()
glad_scripts_deferred = DeferredThroughModel()


class Tag(BaseModel):
    name = CharField(unique=True, primary_key=True)
    
    @staticmethod
    def addTag(tag_name):
        with database:
            Tag.insert(name=tag_name).on_conflict_replace().execute()
    
    @staticmethod
    def deleteTag(tag_name):
        pass
    
    @staticmethod
    def getTags():
        return Tag.select()
    
    @staticmethod
    def addScriptToTag(tag_name, script_name):
        """
        将脚本添加到某个类别中
        @param tag_name: 要添加的类别的名字
        @param script_name: 脚本的名字
        @return:
        """
        with database:
            tag = Tag.get(Tag.name == tag_name)
            if not tag:
                cmds.error(tag, "is not exists")
                return
            script = Script.get_or_none(Script.name == script_name)
            
            if script is None:
                cmds.error(script, "is not exists")
                return
            
            if tag not in script.tags:
                script.tags.add(tag)
    
    @staticmethod
    def removeTagFromScript(tag_name, script_name):
        with database:
            tag = Tag.get(Tag.name == tag_name)
            if not tag:
                cmds.error(script_name, "is not exists")
                return
            script = Script.get_or_none(Script.name == script_name)
            
            if script is None:
                cmds.error(script, "is not exists")
                return
            if tag not in script.tags:
                script.tags.remove(tag)


class Script(BaseModel):
    """
    脚本
    """
    name = CharField(unique=True, primary_key=True)
    
    script_type = IntegerField()
    script_path = CharField()
    
    # 如果是python 模块的话 我们还需要一个 module的path 当运行此脚本的时候 把module path添加到系统path里
    script_module_path = CharField()
    
    tags = ManyToManyField(Tag, backref="Script", through_model=scripts_tags_deferred)
    
    @staticmethod
    def addScript(file_info, typ):
        script_name = file_info.baseName()
        with database:
            Script.insert(
                name=script_name,
                script_path=file_info.absoluteFilePath(),
                script_module_path="",
                script_type=typ
            ).on_conflict_replace().execute()
    
    @staticmethod
    def addPythonModule(file_info):
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
    
    @staticmethod
    def updateScripts():
        """
        注意 此项只有特定用户才可以执行
        @return:
        """
        # 先更新数据
        for child in QDir(scripts_path).entryInfoList(QDir.NoSymLinks | QDir.NoDotAndDotDot | QDir.Files | QDir.Dirs):  # type: QFileInfo
            if child.isDir():
                Script.addPythonModule(child)
            elif child.isFile():
                if child.completeSuffix() == "py":
                    Script.addScript(child, typ=ScriptType.python_script_type)
                elif child.completeSuffix() == "mel":
                    Script.addScript(child, typ=ScriptType.mel_type)
        
        # 然后删除从已经从本地磁盘中移除的脚本
        for script in Script.select():
            script_path = script.script_path
            # 若文件已经从硬盘中删除 那么我们需要删除此脚本的信息 且在关联的表格里也要删除此信息
            if not os.path.exists(script_path):
                deleted_script = Script.get(Script.name == script.name)
                deleted_script.delete_instance(recursive=True, delete_nullable=True)
                deleted_script.save()
    
    @staticmethod
    def getScripts():
        return Script.select()


class GladScripts(BaseModel):
    """
    脚本收藏夹 一个用户用一个收藏夹
    """
    user_name = CharField(unique=True, primary_key=True)
    scripts = ManyToManyField(Script, backref="gladScripts", through_model=glad_scripts_deferred)
    
    @staticmethod
    def addUser(user_name):
        with database:
            GladScripts.insert(user_name=user_name).on_conflict_ignore().execute()
    
    @staticmethod
    def addScriptToUserGlad(user_name, script_name):
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
    
    @staticmethod
    def removeScriptFromUserGlad(user_name, script_name):
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


class ScriptTagsThoughModel(BaseModel):
    script = ForeignKeyField(Script)
    tag = ForeignKeyField(Tag)


class GladScriptsThoughModel(BaseModel):
    script = ForeignKeyField(Script)
    glad_scripts = ForeignKeyField(GladScripts)


scripts_tags_deferred.set_model(ScriptTagsThoughModel)
glad_scripts_deferred.set_model(GladScriptsThoughModel)

with database:
    database.create_tables(
        [
            Script,
            Tag,
            GladScripts,
            ScriptTagsThoughModel,
            GladScriptsThoughModel,
        ], safe=True
    )
