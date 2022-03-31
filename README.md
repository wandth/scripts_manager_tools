
安装方式：
- 拖动install.mel 到maya视口内安装
- scripts_manager_tools.mod 复制 到 maya modules路径下
  - 需要更改 mod里脚本文件的路径


```python
import ScriptsManagerWindow

reload(ScriptsManagerWindow)

ScriptsManagerWindow.createScriptsManagerWindow()
```