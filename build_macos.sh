#! /bin/bash

sudo rm -r macos
mkdir macos
cd ./macos
pyinstaller ../specs/marueditorm.spec
#mkdir ./dist/Marueditor.app/Contents/MacOS/share_os
#cp -r ../file_addon/ ./dist/Marueditor.app/Contents/MacOS/file_addon
#cp -r ../gui_addon/ ./dist/Marueditor.app/Contents/MacOS/gui_addon
#cp -r ../image/ ./dist/Marueditor.app/Contents/MacOS/image
#cp -r ../share/ ./dist/Marueditor.app/Contents/MacOS/share
#cp -r ../language/ ./dist/Marueditor.app/Contents/MacOS/language
#cp ../LICENCE ./dist/Marueditor.app/Contents/MacOS/LICENCE
#cp -r ../share_os/macos/ ./dist/Marueditor.app/Contents/MacOS/share_os/macos
cd ./dist
#7z a -sfx maruediter_standalone_win32.exe ./marueditor
cd ../../