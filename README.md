
安装方式：
- 拖动 drag_me_to_install 到 maya 视口内完成安装



当安装完毕后，对ui的修改 想查看效果 运行此代码 重新加载模块即可

```python
import scripts_manager_tool.ScriptsManagerWindow as ScriptsManagerWindow
reload(ScriptsManagerWindow)


ScriptsManagerWindow.createScriptsManagerWindow()
```