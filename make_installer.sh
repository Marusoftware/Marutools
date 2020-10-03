#! /bin/bash

#py3compile ./installer.py
#mv ./__pycache__/installer.cpython-37.pyc ./installer.pyc
mkdir linux
cd ./linux
pyinstaller ../installer.py
cd ./dist/maruediter/
zip -r ../../src.zip ./*
cd ../../
cp -pR ./dist/installer/* ./
rm -r ./dist
rm -r ./*.spec
cd ..
mkdir windows
cd ./windows
wine py -3 -m PyInstaller --noconsole --uac-admin --uac-uiaccess --icon=./maruediter.png ../installer.py
cd ./dist/maruediter/
zip -r ../../src.zip ./*
cd ../../
cp -pR ./dist/installer/* ./
rm -r ./dist
rm -r ./*.spec
cd ..
#rm installer.pyc
