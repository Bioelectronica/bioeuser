import zmq
import cv2
import threading
from multiprocessing import RawArray
import pdb
import time

names = ['merge1',\
        'merge2',\
        'merge5',\
        'merge6',\
        'waste3',\
        'sample4',\
        'waste7',\
        'sample8']
ports=["7000","7010","7020","7030","8000","8010","8020","8030"]

#arr=RawArray('d',640*3*480*2)
def connect_to_streams(zmqport):
    # Socket to talk to server
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.bind("tcp://{}:{}".format("*",str(zmqport)) )
    socket.subscribe("")
    socket.setsockopt(zmq.CONFLATE,1)
    return socket

def create_windows(p,i,n):
    camstr=n
    camdims=[640,480]
    cv2.namedWindow(camstr,cv2.WINDOW_NORMAL)
    cv2.resizeWindow(camstr, 640, 480)
    cv2.moveWindow(camstr, 100+(i*20), 100)

plist=[]
for i in ports:
    plist.append(connect_to_streams(i))

for i,x in enumerate(ports):
    create_windows(x,i*5,names[i])


def viewdata(camstr,socket):
    dat=socket.recv_pyobj()
    try:
        cv2.imshow(camstr,dat)
    except:
    	t=1
    if cv2.waitKey(1) & 0xFF==ord('q'):
        return False
    return True
gjobs=[]

b=True
b2=True
while(True):
    for i,p in enumerate(ports):
        b=viewdata(names[i],plist[i])
        if b==False:
            b2=False
            break
    if b2==False:
        break
    #time.sleep(2)




