import zmq
import sys
import json
import pdb


if len(sys.argv) < 2:
    print("No arguments given!")
    sys.exit()
elif len(sys.argv) < 3:
    ia = list(sys.argv[-1])
else:
    ia = list(sys.argv[1:])

c1 = zmq.Context()
s1 = c1.socket(zmq.REQ)
s1.connect("tcp://master:5551")

c2 = zmq.Context()
s2 = c2.socket(zmq.REQ)
s2.connect("tcp://slave:5552")

for x in [ia]:
    if sys.argv[1]=='JSON':
        with open(ia[2],'r') as f:
            js=json.load(f)
        if len(ia) > 3:
            ia=[ia[0],ia[1],js,ia[3]]
        else:
            ia=[ia[0],ia[1],js,'']
    s1.send_pyobj(ia)
    s2.send_pyobj(ia)
    print("Sending...")
    msg=s1.recv_string()
    msg2=s2.recv_string()
    print(msg)
    print(msg2)
    
