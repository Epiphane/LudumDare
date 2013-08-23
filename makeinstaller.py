import os

exec(open('exe_setup.py'))

gameName = "LD27"
version = "0.0.1"

f = open("dist/installer.nsi","w")

main = "dist/"
path = ""

f.write("Name \""+gameName+"Installer\"\n")
f.write("OutFile \""+gameName+"_"+version+".exe\"\n")
f.write("InstallDir $PROGRAMFILES\\"+gameName+"\n")
f.write("DirText \"This will install "+gameName+" on your computer. Choose a directory\"\n")
f.write("Section \"\" ;No components page, name is not important\n")
dirs = []

def loadpics(main,path):
	pics = []
	pics_raw = os.listdir(main+path)
	if path != "":
		f.write("\tCreateDirectory $INSTDIR"+path+"\n")
		global dirs
		dirs.append(path)
	f.write("\tSetOutPath $INSTDIR"+path+"\n")
	for pic in pics_raw:
		if pic[0] == ".": continue
		try:
			newpics = loadpics(main,path+"\\"+pic)
			for newpic in newpics:
				pics.append(newpic)
			f.write("\tSetOutPath $INSTDIR"+path+"\n")
		except:
			pics.append(path+"\\"+pic+"\n")
			if path != "": f.write("\tFile "+path[1:]+"\\"+pic+"\n")
			else:
					if pic != "installer.nsi": f.write("\tFile "+pic+"\n")

	return pics

pics = loadpics(main,path)
for pic in pics:
	pic = pic[1:]
f.write("\tWriteUninstaller $INSTDIR\Uninstall.exe\n")
f.write("SectionEnd\n")
f.write("Section \"Uninstall\"\n")
f.write("\tDelete $INSTDIR\Uninstall.exe\n")
for pic in pics:
	pic = pic[1:]
	f.write("\tDelete $INSTDIR\\"+pic)
for d in range(len(dirs)):
	f.write("\tRMDir $INSTDIR"+dirs[len(dirs)-1-d]+"\n")
f.write("\tRMDir $INSTDIR\n")
f.write("SectionEnd")

f.close()
