
DEBUG = True
SECRET_KEY = 'something secret'

#REDIS_HOST = '192.168.0.10'
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379

BROKER_URL = 'redis://%s:%s/0' % (REDIS_HOST, REDIS_PORT)

SOCKETIO_CHANNEL = 'tail-message'
MESSAGES_KEY = 'tail'
CHANNEL_NAME = 'tail-channel'

SOCKETIO_CHANNEL_2 = 'val-message'
MESSAGES_KEY_2 = 'val'
CHANNEL_NAME_2 = 'val-channel'

dataPath = "C:/data/lahan/input/LC81010622015016DKI00L1TV10/"
modelPath = "C:/data/lahan/model/DATATRAIN_decisionTree.pkl"
shpPath = "C:/data/lahan/shp"
outputPath = "C:/data/lahan/hasil/"


