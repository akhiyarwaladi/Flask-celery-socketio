import time
from datetime import datetime
from celery import Celery
from flask import Flask, render_template, request, flash
from redis import StrictRedis
from socketio import socketio_manage
from socketio.namespace import BaseNamespace
from celery.task.control import revoke
import urllib2
from assets import assets
import config
import celeryconfig
import os
from sklearn.externals import joblib


import arcpy
from arcpy.sa import *
import pandas as pd
import numpy as np
import os.path
import ftpClient as ft
import shutil

redis = StrictRedis(host=config.REDIS_HOST)
redis.delete(config.MESSAGES_KEY)
redis.delete(config.MESSAGES_KEY_2)
# celery = Celery(__name__)
# celery.config_from_object(celeryconfig)

app = Flask(__name__)
app.config.from_object(config)
assets.init_app(app)

app.config['SECRET_KEY'] = 'top-secret!'
app.config['SOCKETIO_CHANNEL'] = 'tail-message'
app.config['MESSAGES_KEY'] = 'tail'
app.config['CHANNEL_NAME'] = 'tail-channel'

app.config['SOCKETIO_CHANNEL_2'] = 'val-message'
app.config['MESSAGES_KEY_2'] = 'val'
app.config['CHANNEL_NAME_2'] = 'val-channel'

app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

# Initialize Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)


def internet_on():
    for timeout in [1,5,10,15]:
        try:
            response=urllib2.urlopen('http://google.com',timeout=timeout)
            return True
        except urllib2.URLError as err: pass
    return False

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if(internet_on()):
            if redis.llen(config.MESSAGES_KEY):
                flash('Task is already running', 'error')
            # elif(redis.llen(config.MESSAGES_KEY) == 0):
            #     flash('Task is finished', 'success')
            else:
                tail.delay()
                flash('Task started. Please wait until complete', 'info')
        else:
            flash('Internet connection is bad. Please pay your internet bill :)','error')

    return render_template('index.html')

@app.route('/socket.io/<path:remaining>')
def socketio(remaining):
    socketio_manage(request.environ, {
        '/tail': TailNamespace
    })
    return app.response_class()

@app.route('/stop', methods=['GET', 'POST'])
def stop():
    if request.method == 'POST':
        tail.delay()
    return render_template('index.html')

@celery.task
def tail():

    msg = str(datetime.now()) + '\t' + "Importing Library ... \n"
    redis.rpush(config.MESSAGES_KEY, msg)
    redis.publish(config.CHANNEL_NAME, msg)
    
    arcpy.CheckOutExtension("spatial")
#    stat = ft.downloadFile()
    filename = "L8U1T101062m_160115_geo.ers"
    filenameOut = "L8U1T101062m_160115_geo_classified.TIF"
    dataPath =  config.dataPath + filename
    modelPath = config.modelPath
    shpPath = config.shpPath

    outFolder = config.outputPath + filename.split(".")[0]
    if(os.path.exists(outFolder)):
        shutil.rmtree(outFolder)
    os.makedirs(outFolder)
    outputPath = outFolder + "/" + filenameOut


    print ("converting b3")
    if(os.path.exists(dataPath + "TOA_B3" + ".TIF")):
        os.remove(dataPath + "TOA_B3" + ".TIF")

    b_green = arcpy.Raster( dataPath  + "/B3" ) * 1.0
    #b_green_mask = Con((mask >= 1) & (mask <= 7), 1, b_green)
    #b_green_mask = SetNull(b_green_mask == 1, b_green_mask)
    print ("saving b3")
    msg = str(datetime.now()) + '\t' + "saving b3 \n"
    redis.rpush(config.MESSAGES_KEY, msg)
    redis.publish(config.CHANNEL_NAME, msg)
    b_green.save(dataPath + "TOA_B3" + ".TIF" )
    del b_green

    print ("converting b5")
    if(os.path.exists(dataPath + "TOA_B5" + ".TIF")):
        os.remove(dataPath + "TOA_B5" + ".TIF")

    b_nir = arcpy.Raster( dataPath  + "/B5" ) * 1.0
    #b_nir_mask = Con((mask >= 1) & (mask <= 7), 1, b_nir)
    #b_nir_mask = SetNull(b_nir_mask == 1, b_nir_mask)
    print ("saving b5")
    msg = str(datetime.now()) + '\t' + "saving b5 \n"
    redis.rpush(config.MESSAGES_KEY, msg)
    redis.publish(config.CHANNEL_NAME, msg)
    b_nir.save( dataPath +  "TOA_B5" + ".TIF" )
    del b_nir

    print ("converting b6")
    if(os.path.exists(dataPath + "TOA_B6" + ".TIF")):
       os.remove(dataPath + "TOA_B6" + ".TIF")

    b_swir1 = arcpy.Raster( dataPath + "/B6") * 1.0
    #b_swir1_mask = Con((mask >= 1) & (mask <= 7), 1, b_swir1)
    #b_swir1_mask = SetNull(b_swir1_mask == 1, b_swir1_mask)
    msg = str(datetime.now()) + '\t' + "saving b6 \n"
    redis.rpush(config.MESSAGES_KEY, msg)
    redis.publish(config.CHANNEL_NAME, msg)
    print ("saving b6")
    b_swir1.save( dataPath + "TOA_B6" + ".TIF" )
    del b_swir1

    msg = str(datetime.now()) + '\t' + "Processing file "+filename+"\n"
    redis.rpush(config.MESSAGES_KEY, msg)
    redis.publish(config.CHANNEL_NAME, msg)

    rasterarrayband6 = arcpy.RasterToNumPyArray(dataPath + "TOA_B3.TIF")
    rasterarrayband5 = arcpy.RasterToNumPyArray(dataPath + "TOA_B5.TIF")
    rasterarrayband3 = arcpy.RasterToNumPyArray(dataPath + "TOA_B6.TIF")
    
    print("Change raster format to numpy array")
    data = np.array([rasterarrayband6.ravel(), rasterarrayband5.ravel(), rasterarrayband3.ravel()], dtype=np.int16)
    data = data.transpose()

    del rasterarrayband5
    del rasterarrayband3

    print("Change to dataframe format")

    msg = str(datetime.now()) + '\t' + "Change to dataframe format \n"
    redis.rpush(config.MESSAGES_KEY, msg)
    redis.publish(config.CHANNEL_NAME, msg)
    #time.sleep(1)

    columns = ['band3','band5', 'band6']
    df = pd.DataFrame(data, columns=columns)
    del data

    print("Split data to 20 chunks ")
    msg = str(datetime.now()) + '\t' + "Split data to 20 chunks \n"
    redis.rpush(config.MESSAGES_KEY, msg)
    redis.publish(config.CHANNEL_NAME, msg)
    #time.sleep(1)

    df_arr = np.array_split(df, 20)
    clf = joblib.load(modelPath) 
    kelasAll = []
    for i in range(len(df_arr)):
        
        print ("predicting data chunk-%s\n" % i)
        msg = str(datetime.now()) + '\t' + "predicting data chunk-%s\n" % i
        redis.rpush(config.MESSAGES_KEY, msg)
        redis.publish(config.CHANNEL_NAME, msg)

        msg2 = i
        redis.rpush(config.MESSAGES_KEY_2, msg2)
        redis.publish(config.CHANNEL_NAME_2, msg2)
        #time.sleep(1)
        kelas = clf.predict(df_arr[i])
        dat = pd.DataFrame()
        dat['kel'] = kelas
        print ("mapping to integer class")
        msg = str(datetime.now()) + '\t' + "mapping to integer class \n"
        redis.rpush(config.MESSAGES_KEY, msg)
        redis.publish(config.CHANNEL_NAME, msg)
        #time.sleep(1)
        mymap = {'awan':1, 'air':2, 'tanah':3, 'vegetasi':4}
        dat['kel'] = dat['kel'].map(mymap)

        band1Array = dat['kel'].values
        band1Array = np.array(band1Array, dtype = np.uint8)
        print ("extend to list")
        msg = str(datetime.now()) + '\t' + "extend to list \n"
        redis.rpush(config.MESSAGES_KEY, msg)
        redis.publish(config.CHANNEL_NAME, msg)
        #time.sleep(1)
        #kelasAllZeros[] = band1Array
        kelasAll.extend(band1Array.tolist())
        print(kelasAll[1:10])
        #del band1Array

    del df_arr
    del clf
    del kelas
    del dat
    del band1Array

    print ("change list to np array")
    msg = str(datetime.now()) + '\t' + "change list to np array \n"
    redis.rpush(config.MESSAGES_KEY, msg)
    redis.publish(config.CHANNEL_NAME, msg)

    kelasAllArray = np.array(kelasAll, dtype=np.uint8)

    print ("reshaping np array")
    msg = str(datetime.now()) + '\t' + "reshaping np array \n"
    redis.rpush(config.MESSAGES_KEY, msg)
    redis.publish(config.CHANNEL_NAME, msg)

    band1 = np.reshape(kelasAllArray, (-1, rasterarrayband6[0].size))
    band1 = band1.astype(np.uint8)

    raster = arcpy.Raster(dataPath + "TOA_B6.TIF")
    inputRaster = dataPath + "TOA_B6.TIF"

    spatialref = arcpy.Describe(inputRaster).spatialReference
    cellsize1  = raster.meanCellHeight
    cellsize2  = raster.meanCellWidth
    extent     = arcpy.Describe(inputRaster).Extent
    pnt        = arcpy.Point(extent.XMin,extent.YMin)

    del raster
    del rasterarrayband6
    del kelasAllArray

    # save the raster
    print ("numpy array to raster ..")
    msg = str(datetime.now()) + '\t' + "numpy array to raster .. \n"
    redis.rpush(config.MESSAGES_KEY, msg)
    redis.publish(config.CHANNEL_NAME, msg)

    out_ras = arcpy.NumPyArrayToRaster(band1, pnt, cellsize1, cellsize2)

    arcpy.CheckOutExtension("Spatial")
    print ("define projection ..")
    msg = str(datetime.now()) + '\t' + "define projection ..\n"
    redis.rpush(config.MESSAGES_KEY, msg)
    redis.publish(config.CHANNEL_NAME, msg)

    arcpy.CopyRaster_management(out_ras, outputPath)
    arcpy.DefineProjection_management(outputPath, spatialref)

    print("Masking Cloud")
    mask = Raster(os.path.dirname(dataPath) + "/" + filename.split(".")[0] + "_cm.ers")
    inRas = Raster(outputPath)
    inRas_mask = Con((mask == 1), 1, Con((mask == 2), 1, Con((mask == 11), 1, 0)))
    inRas_mask.save(os.path.dirname(outputPath) + "/" + filenameOut.split(".")[0] + "_mask.TIF")
    mask2 = IsNull(inRas_mask)
    inRas2 = Con((mask2 == 1), 0, inRas_mask)
    inRas2.save(os.path.dirname(outputPath) + "/" + filenameOut.split(".")[0] + "_mask2.TIF")
    inRas_mask2 = SetNull(inRas2 == 1, inRas)
    inRas_mask2.save(os.path.dirname(outputPath) + "/" + filenameOut.split(".")[0] + "_maskCloud.TIF")

    del mask
    del inRas
    del inRas_mask
    del inRas_mask2

    print("Masking with shp indonesia")
    arcpy.CheckOutExtension("Spatial")
    inMaskData = os.path.join(shpPath, "INDONESIA_PROP.shp")
    inRasData = Raster(os.path.dirname(outputPath) + "/" + filenameOut.split(".")[0] + "_maskCloud.TIF")
    outExtractByMask = ExtractByMask(inRasData, inMaskData)
    print("Saving in: " + str(os.path.dirname(outputPath) + "/" + filenameOut.split(".")[0] + "_maskShp.TIF"))
    outExtractByMask.save(os.path.dirname(outputPath) + "/" + filenameOut.split(".")[0] + "_maskShp.TIF")

    del out_ras
    del band1
    del spatialref
    del extent
    arcpy.Delete_management("in_memory")

    print ("Finished ..")
    msg = str(datetime.now()) + '\t' + "Finished ... \n"
    redis.rpush(config.MESSAGES_KEY, msg)
    redis.publish(config.CHANNEL_NAME, msg)

    redis.delete(config.MESSAGES_KEY)
    redis.delete(config.MESSAGES_KEY_2)

class TailNamespace(BaseNamespace):
    def listener(self):
        # Emit the backlog of messages
        messages = redis.lrange(config.MESSAGES_KEY, 0, -1)        
        messages2 = redis.lrange(config.MESSAGES_KEY_2, 0, -1)

        print(messages2)
        self.emit(config.SOCKETIO_CHANNEL, ''.join(messages))
        self.emit(config.SOCKETIO_CHANNEL_2, ''.join(messages2))

        self.pubsub.subscribe(config.CHANNEL_NAME)
        self.pubsub.subscribe(config.CHANNEL_NAME_2)
        i=8
        for m in self.pubsub.listen():
            if m['type'] == 'message':
                self.emit(config.SOCKETIO_CHANNEL, m['data'])
                self.emit(config.SOCKETIO_CHANNEL_2, i)
                i=i+1

    def on_subscribe(self):
        self.pubsub = redis.pubsub()
        self.spawn(self.listener)
