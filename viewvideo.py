import zmq
import cv2
import threading
from multiprocessing import RawArray
import pdb
import time
import os
import logging


#arr=RawArray('d',640*3*480*2)
def connect_to_streams(zmqport):
    # Socket to talk to server
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.bind("tcp://{}:{}".format("*",str(zmqport)) )
    socket.subscribe("")
    #poller=zmq.Poller()
    #poller.register(socket,zmq.POLLIN)
    #socket.setsockopt(zmq.CONFLATE,1)
    return (socket,context)

def create_windows(p,i,n):
    camstr=n
    camdims=[640,480]
    cv2.namedWindow(camstr,cv2.WINDOW_NORMAL)
    cv2.resizeWindow(camstr, 640, 480)
    cv2.moveWindow(camstr, 100+(i*20), 100)

def getdata(camstr,socket):
    try:
        logging.info(camstr)
        dat=socket.recv_pyobj(flags=zmq.NOBLOCK)
        fname='/tmp/'+camstr+'.jpg'
        cv2.imwrite(fname,dat,[int(cv2.IMWRITE_JPEG_QUALITY),90])
        logging.info(camstr+'done with img')
        return True
    except zmq.error.Again as ef:
        return False
    except Exception as e:
        logging.exception("Exception caught")
        return False

def viewdata(camstr):
    try:
        im=cv2.imread('/tmp/'+camstr+'.jpg')
        #pdb.set_trace()
        cv2.imshow(camstr,im)
    except Exception as e:
        logging.exception("Exception caught")
    if cv2.waitKey(10) & 0xFF==ord('q'):
        return False
    return True

names = ['merge1',\
        'merge2',\
        'merge5',\
        'merge6',\
        'waste3',\
        'sample4',\
        'waste7',\
        'sample8']
ports=["7000","7010","7020","7030","8000","8010","8020","8030"]

logging.basicConfig(format='%(asctime)s %(threadName)s %(message)s',\
filename='/home/bioeuser1/logs/vidlog.log',\
level=logging.DEBUG)

time.sleep(30)
pclist=[]
imbool=[]
imlist=[]


for i in ports:
    pclist.append(connect_to_streams(i))

for i,x in enumerate(ports):
    create_windows(x,i*5,names[i])

plist=[x[0] for x in pclist]
clist=[x[1] for x in pclist]
#polist=[x[2] for x in pclist]

gjobs=[]

b=True
b2=True
while(os.path.isfile('/home/bioeuser1/expdone')==False):
    gjobs=[]
    for idx,camOI in enumerate(names):
        g=threading.Thread(target=getdata,name=camOI,args=(camOI,plist[idx],))
        gjobs.append(g)
    for k in gjobs:
        k.start()
    for k in gjobs:
        k.join()
    for i,p in enumerate(ports):
        b=viewdata(names[i])
        if b==False:
            b2=False
            break
    if b2==False:
        break
    #time.sleep(2)
os.remove('/home/bioeuser1/expdone')

for pr in plist:
    pr.close()
for ct in clist:
    ct.term()


