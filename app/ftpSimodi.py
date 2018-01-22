from ftplib import FTP
import os
from datetime import datetime
import shutil
def downloadFile(liScene):
	boolScene = False
	print "Sudah diproses " + str(liScene)

	tupDate = datetime.now()
	print tupDate.year
	print tupDate.strftime('%j')
	#print now.year, now.month, now.day, now.hour, now.minute, now.second # check every datetime detail
	ftp = FTP( )
	ftp.connect(host='localhost', port=21, timeout=123456)
	ftp.login(user='akhiyarwaladi', passwd='rickss12')
	#ftp.retrlines('LIST') # use to check file after connected
	ftp.cwd('L8_REFLECTANCE_MS')
	year = '2015'
	ftp.cwd(year)
	month = '2015_01'
	ftp.cwd(month)
	for scene in ftp.nlst():
		print scene
		# jika scene termasuk kedalam list yang telah diproses
		if scene in liScene:
			print "scene " + str(scene) + " sudah diproses"
			# lanjut lihat folder scene yang lainnya
			continue;
		# jika tidak termasuk maka set boolean bahwa ada data yang akan diproses
		boolScene = True
		ftp.cwd(scene)
		if(os.path.exists("C:/data/lahan/input/" + scene)):
			shutil.rmtree("C:/data/lahan/input/" + scene)
		os.makedirs("C:/data/lahan/input/" + scene)
		fileScene = ftp.nlst()
		fileScene2 = [img for img in fileScene if img.endswith("_geo") or img.endswith("_geo.ers") or img.endswith("_geo_cm") or 
		img.endswith("_geo_cm.ers")]
		for file in fileScene2:
			print file

			filename = file #replace with your file in the directory ('directory_name')
			localfile = open(filename, 'wb')


			ftp.retrbinary('RETR ' + filename, localfile.write, 1024)
			localfile.close()


			os.rename(filename, "C:/data/lahan/input/" + scene + "/" + file)

		break;	

		ftp.cwd("../")

	sceneNow = os.listdir("C:/data/lahan/input/" + scene)

	filenameNow = [img for img in sceneNow if 'geo.ers' in img]
	print filenameNow
	return filenameNow[0], scene, boolScene, year, month