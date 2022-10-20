# coding=utf-8
import os
import sys

from maya import utils, cmds


def addLibPath() :
    module_path = cmds.getModulePath(moduleName = "scripts_manager_tools")
    [sys.path.append(third_lib_path) for third_lib_path in [
        os.path.join(module_path, "third_lib").replace('\\', '/'),
        os.path.join(module_path, "src").replace('\\', '/')
    ] if third_lib_path not in sys.path]


def main() :
    addLibPath()

    import scripts_manager_tool.ScriptsManagerWindow as ScriptsManagerWindow
    reload(ScriptsManagerWindow)
    ScriptsManagerWindow.createToolButton()
    ScriptsManagerWindow.createScriptsManagerWindow()


if __name__ == "__main__" :
    utils.executeDeferred(main)
