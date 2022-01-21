# -*- coding: utf-8 -*-

from cx_Freeze import setup, Executable
import requirements

uuid = "{3c03a355-b5b0-4da1-804c-02869b342ecc}"

shortcut_table = [
    ("DesktopShortcut",        # Shortcut
     "DesktopFolder",          # Directory_
     requirements.name,        # Name
     "TARGETDIR",              # Component_
     "[TARGETDIR]marueditor.exe",# Target
     None,                     # Arguments
     None,                     # Description
     None,                     # Hotkey
     None,# Icon
     None,                     # IconIndex
     None,                     # ShowCmd
     'TARGETDIR'               # WkDir
     )
]

# Table dictionary
msi_data = {'Shortcut': shortcut_table}

# 追加モジュールで必要なものを packages に入れる
build_exe_options = {'packages': requirements.require,
                     'excludes': requirements.exclude,
                     'includes': [],
                     'include_files': requirements.include_files,
                     'optimize':2
}

bdist_msi_options = {'upgrade_code': uuid,
                     'add_to_path': False,
                     'data': msi_data
}

options = {
    'build_exe': build_exe_options,
    'bdist_msi': bdist_msi_options
}

import sys
base = 'Win32GUI' if sys.platform == 'win32' else None

marueditor = Executable(
                script="marueditor.py",
                targetName="marueditor.exe",
                base=base,
                icon=requirements.icon,
                shortcutName =requirements.name,
                shortcutDir ="ProgramMenuFolder"
                )

# セットアップ
setup(name=requirements.name,
      version=requirements.version,
      author=requirements.author,
      url=requirements.url,
      description=requirements.description,
      options=options,
      executables=[marueditor]
      )
