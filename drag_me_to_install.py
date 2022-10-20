# coding=utf-8
import codecs
import os
import json
import sys


def onMayaDroppedPythonFile(*args, **kwargs):
    """This function is only supported since Maya 2017 Update 3"""
    pass


def _onMayaDropped():
    current_path = os.path.dirname(__file__)
    # 若是外包 则需要拖动安装
    config_full_path = current_path + "/src/scripts_manager_tool/resource/" + "config.json"
    module_name = json.load(open(config_full_path, "r"))["module_name"]
    
    print module_name
    
    module_full_path = filter(lambda module: "Documents" in module, os.getenv("MAYA_MODULE_PATH").split(";"))[0] + "/" + module_name + ".mod"
    
    if not os.path.exists(module_full_path.rsplit("/", 1)[0]):
        os.makedirs(module_full_path.rsplit("/", 1)[0])
    
    with codecs.open(module_full_path, 'w', 'utf-8') as f:
        f.write("+ {tool_name} 1.0 {current_path}".format(tool_name=module_name, current_path=current_path))
    
    # 安装好 执行添加菜单的脚本
    [sys.path.append(third_lib_path) for third_lib_path in [
        current_path + "/" + "src",
        current_path + "/" + "third_lib"
    ] if third_lib_path not in sys.path]
    
    import scripts_manager_tool.ScriptsManagerWindow as script_manager_window
    reload(script_manager_window)
    
    # 此处为在状态栏添加按钮 此按钮的作用就是点击创建脚本管理器
    script_manager_window.createToolButton()


_onMayaDropped()
