#! /bin/bash

cd build
cd ./linux
sudo rm -r ./marueditor/usr/share/marueditor/
mkdir ./marueditor/usr/share/marueditor/
mkdir ./marueditor/usr/share/marueditor/share_os
cp -r ../file_addon/ ./marueditor/usr/share/marueditor/file_addon
cp -r ../gui_addon/ ./marueditor/usr/share/marueditor/gui_addon
cp -r ../image/ ./marueditor/usr/share/marueditor/image
cp -r ../share/ ./marueditor/usr/share/marueditor/share
cp -r ../language/ ./marueditor/usr/share/marueditor/language
cp -r ../share_os/linux64/ ./marueditor/usr/share/marueditor/share_os/linux64
cp -r ../share_os/linux64/ ./marueditor/usr/share/marueditor/share_os/linux32
cp -r ../share_os/linux64/ ./marueditor/usr/share/marueditor/share_os/raspi
sudo chmod -R 777 ./marueditor/usr/
rm ./marueditor/DEBIAN/control
cp ./all/control ./marueditor/DEBIAN/control
#pyarmor obfuscate -O ./marueditor/usr/share/marueditor --exact --platform linux.x86_64 ../marueditor.py
cp ../marueditor.py ./marueditor/usr/share/marueditor/
fakeroot dpkg-deb --build marueditor ./all
#fakeroot dpkg-deb --build marueditor ./all
cd all
fakeroot alien -r ./marueditor*.deb
fakeroot alien -t ./marueditor*.deb
cd ../../

# cd 64
# fakeroot alien -r ./marueditor*.deb
# fakeroot alien -t ./marueditor*.deb
# cd ..
# rm ./marueditor/usr/share/marueditor/pytransform/_pytransform.so
# rm ./marueditor/DEBIAN/control
# rm -r ./marueditor/usr/share/marueditor/share_os/linux64
# cp ./32/control ./marueditor/DEBIAN/control
# cp -r ../share_os/linux32/ ./marueditor/usr/share/marueditor/share_os/linux32
# pyarmor obfuscate -O ./marueditor/usr/share/marueditor --exact --platform linux.x86 ../marueditor.py
# fakeroot dpkg-deb --build marueditor ./32/
# cd 32
# fakeroot alien -r ./marueditor*.deb
# fakeroot alien -t ./marueditor*.deb
# cd ..
# rm ./marueditor/DEBIAN/control
# cp ./armv7/control ./marueditor/DEBIAN/control
# pyarmor obfuscate -O ./marueditor/usr/share/marueditor --exact --platform linux.armv7 ../marueditor.py
# fakeroot dpkg-deb --build marueditor ./armv7/
# cd ..
sudo rm -r win32
mkdir win32
cd ./win32
wine py -3.8-32 -m PyInstaller --noconsole ../specs/marueditorw3.spec
mkdir ./dist/marueditor/share_os
cp -r ../file_addon/ ./dist/marueditor/file_addon
cp -r ../gui_addon/ ./dist/marueditor/gui_addon
cp -r ../image/ ./dist/marueditor/image
cp -r ../share/ ./dist/marueditor/share
cp -r ../language/ ./dist/marueditor/language
cp -r ../share_os/win32/ ./dist/marueditor/share_os/win32
cd ./dist
7z a -sfx maruediter_standalone_win32.exe ./marueditor
cd ../../
sudo rm -r win64
mkdir win64
cd ./win64
wine py -3.8-64 -m PyInstaller --noconsole ../specs/marueditorw6.spec
mkdir ./dist/marueditor/share_os
cp -r ../file_addon/ ./dist/marueditor/file_addon
cp -r ../gui_addon/ ./dist/marueditor/gui_addon
cp -r ../image/ ./dist/marueditor/image
cp -r ../share/ ./dist/marueditor/share
cp -r ../language/ ./dist/marueditor/language
cp -r ../share_os/win64/ ./dist/marueditor/share_os/win64
cd ./dist
7z a -sfx maruediter_standalone_win64.exe ./marueditor
cd ../../
#sudo rm -r macos
#mkdir macos
#cd ./macos
#darling shell python3 -m PyInstaller --noconsole --onefile ../marueditor.py
#mkdir ./dist/marueditor/share_os
#cp -r ../file_addon/ ./dist/marueditor/file_addon
#cp -r ../gui_addon/ ./dist/marueditor/gui_addon
#cp -r ../image/ ./dist/marueditor/image
#cp -r ../share/ ./dist/marueditor/share
#cp -r ../language/ ./dist/marueditor/language
#cp -r ../share_os/macos/ ./dist/marueditor/share_os/macos
