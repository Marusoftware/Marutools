# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['../marueditor.py'],
             pathex=['/Volumes/Shared/Program/Marutools'],
             binaries=[],
             datas=[("../file_addon", "file_addon"),("../gui_addon", "gui_addon"),("../image", "image"),("../share", "share"),("../share_os/macos","share_os/macos"),("../language/", "language"),("../LICENCE", ".")],
             hiddenimports=["babel", "pytz", "psutil", "babel.numbers", "numpy", "PIL", "PIL.ImageTk", "tkinter.tix"],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='Marueditor',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False )
app = BUNDLE(exe,
             name='Marueditor.app',
             icon="../image/marueditor.ico",
             bundle_identifier=None)
