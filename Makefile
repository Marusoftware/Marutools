
all:
	make linux
	make windows
linux:
	make linux32
	make linux64
	make linuxarmv7
windows:
	make win64
	make win32
