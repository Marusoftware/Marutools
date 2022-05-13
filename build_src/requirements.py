name = "Marutools"
version = "1.0.0b"
description = "Marutools Beta"
author = "Marusoftware"
url = "https://marusoftware.net/documents/marutools.html"
icon = "image/marueditor.ico"
require=["os", "getpass", "json", "locale", "platform", "sys", "tkinter", "PIL", "subprocess","time", "argparse", "chardet","importlib","random","logging","string","traceback","ttkthemes"]
exclude=["scipy"]
import platform
if platform.system() == "Linux":
    require.append("tkfilebrowser")
include_files=["share/","libmarusoftware/","share_os/","language/","image/","addons/", "LICENCE"]