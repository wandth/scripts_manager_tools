import inspect
import os

from pathlib import Path


def getResourcePath():
    return Path(os.path.dirname(inspect.getsourcefile(inspect.currentframe())))
