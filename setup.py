# -*- coding: utf-8 -*-

from cx_Freeze import setup, Executable

name = "Marueditor"
version = "0.0.2b"
description = "Marueditor Beta"
author = "Marusoftware"
url = "https://github.com/Marusoftware/Marutools"

# UUIDは一度決めたら変更しない
upgrade_code = "{3c03a355-b5b0-4da1-804c-02869b342ecc}"

# ----------------------------------------------------------------
# セットアップ
# ----------------------------------------------------------------
shortcut_table = [
    ('DesktopShortcut',        # Shortcut
     'DesktopFolder',          # Directory_
     name,               # Name
     'TARGETDIR',              # Component_
     f'[TARGETDIR]marueditor.exe',   # Target
     None,                     # Arguments
     None,                     # Description
     None,                     # Hotkey
     None,                     # Icon
     None,                     # IconIndex
     None,                     # ShowCmd
     'TARGETDIR',              # WkDir
    )
    ]

# Table dictionary
msi_data = {'Shortcut': shortcut_table}

# 追加モジュールで必要なものを packages に入れる
build_exe_options = {'packages': open("requirements_module.txt").read().split(),
                     'excludes': [],
                     'includes': [],
                     'include_files': ["share/","libtools/","share_os/win32/","share_os/win64/","language/","image/","file_addon/","gui_addon"]
}

bdist_msi_options = {'upgrade_code': upgrade_code,
                     'add_to_path': False,
                     'data': msi_data
}

options = {
    'build_exe': build_exe_options,
    'bdist_msi': bdist_msi_options
}

# CUI : None
base = None 
# GUI :  'Win32GUI' if sys.platform == 'win32' else None

icon = "image/marueditor.ico"

# exe にしたい python ファイルを指定
exe = Executable(script="marueditor.py",
                 targetName="marueditor.exe",
                 base=base,
                 icon=icon
                 )

# セットアップ
setup(name=name,
      version=version,
      author=author,
      url=url,
      description=description,
      options=options,
      executables=[exe]
      )
