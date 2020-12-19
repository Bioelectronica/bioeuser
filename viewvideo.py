import zmq
import cv2
import threading
from multiprocessing import RawArray
import pdb
import time

   
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

def create_windows(p,i):
    camstr=str(p)
    camdims=[640,480]
    cv2.namedWindow(camstr,cv2.WINDOW_NORMAL)
    cv2.resizeWindow(camstr, 640, 480)
    cv2.moveWindow(camstr, 100+i, 100)

plist=[]
for i in ports:
    plist.append(connect_to_streams(i))

for i,x in enumerate(ports):
    create_windows(x,i*5)


def viewdata(camstr,socket):
    dat=socket.recv_pyobj()
    #pdb.set_trace()
    cv2.imshow(camstr,dat)
    if cv2.waitKey(1) & 0xFF==ord('q'):
        return False
    return True
gjobs=[]

b=True
b2=True
while(True):
    for i,p in enumerate(ports):
        b=viewdata(p,plist[i])
        if b==False:
            b2=False
            break
    if b2==False:
        break
    #time.sleep(2)




