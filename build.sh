#! /bin/bash

cd ./linux
sudo rm -r ./maruediter/usr/share/maruediter/
mkdir ./maruediter/usr/share/maruediter/
mkdir ./maruediter/usr/share/maruediter/share_os
cp -r ../file_addon/ ./maruediter/usr/share/maruediter/file_addon
cp -r ../gui_addon/ ./maruediter/usr/share/maruediter/gui_addon
cp -r ../image/ ./maruediter/usr/share/maruediter/image
cp -r ../share/ ./maruediter/usr/share/maruediter/share
cp -r ../language/ ./maruediter/usr/share/maruediter/language
cp -r ../share_os/linux64/ ./maruediter/usr/share/maruediter/share_os/linux64
sudo chmod -R 777 ./maruediter/usr/
rm ./maruediter/DEBIAN/control
cp ./64/control ./maruediter/DEBIAN/control
pyarmor obfuscate -O ./maruediter/usr/share/maruediter --exact --platform linux.x86_64 ../maruediter.py
fakeroot dpkg-deb --build maruediter ./64
#fakeroot dpkg-deb --build maruediter ./64
cd 64
fakeroot alien -r ./maruediter*.deb
fakeroot alien -t ./maruediter*.deb
cd ..
rm ./maruediter/usr/share/maruediter/pytransform/_pytransform.so
rm ./maruediter/DEBIAN/control
rm -r ./maruediter/usr/share/maruediter/share_os/linux64
cp ./32/control ./maruediter/DEBIAN/control
cp -r ../share_os/linux32/ ./maruediter/usr/share/maruediter/share_os/linux32
pyarmor obfuscate -O ./maruediter/usr/share/maruediter --exact --platform linux.x86 ../maruediter.py
fakeroot dpkg-deb --build maruediter ./32/
cd 32
fakeroot alien -r ./maruediter*.deb
fakeroot alien -t ./maruediter*.deb
cd ..
rm ./maruediter/DEBIAN/control
cp ./armv7/control ./maruediter/DEBIAN/control
pyarmor obfuscate -O ./maruediter/usr/share/maruediter --exact --platform linux.armv7 ../maruediter.py
fakeroot dpkg-deb --build maruediter ./armv7/
cd ..
sudo rm -r win32
mkdir win32
cd ./win32
wine py -3.8-32 -m PyInstaller --noconsole ../specs/maruediterw3.spec
mkdir ./dist/maruediter/share_os
cp -r ../file_addon/ ./dist/maruediter/file_addon
cp -r ../gui_addon/ ./dist/maruediter/gui_addon
cp -r ../image/ ./dist/maruediter/image
cp -r ../share/ ./dist/maruediter/share
cp -r ../language/ ./dist/maruediter/language
cp -r ../share_os/win32/ ./dist/maruediter/share_os/win32
cd ./dist
7z a -sfx maruediter_standalone_win32.exe ./maruediter
cd ../../
sudo rm -r win64
mkdir win64
cd ./win64
wine py -3.8-64 -m PyInstaller --noconsole ../specs/maruediterw6.spec
mkdir ./dist/maruediter/share_os
cp -r ../file_addon/ ./dist/maruediter/file_addon
cp -r ../gui_addon/ ./dist/maruediter/gui_addon
cp -r ../image/ ./dist/maruediter/image
cp -r ../share/ ./dist/maruediter/share
cp -r ../language/ ./dist/maruediter/language
cp -r ../share_os/win64/ ./dist/maruediter/share_os/win64
cd ./dist
7z a -sfx maruediter_standalone_win64.exe ./maruediter
cd ../../
#sudo rm -r macos
#mkdir macos
#cd ./macos
#darling shell python3 -m PyInstaller --noconsole --onefile ../maruediter.py
#mkdir ./dist/maruediter/share_os
#cp -r ../file_addon/ ./dist/maruediter/file_addon
#cp -r ../gui_addon/ ./dist/maruediter/gui_addon
#cp -r ../image/ ./dist/maruediter/image
#cp -r ../share/ ./dist/maruediter/share
#cp -r ../language/ ./dist/maruediter/language
#cp -r ../share_os/macos/ ./dist/maruediter/share_os/macos
