#!/usr/bin/python
from multiprocessing import Process
import zmq

def f01(name):
    context = zmq.Context()
    footage_socket = context.socket(zmq.SUB)
    footage_socket.bind('tcp://*:9995')
    footage_socket.setsockopt_string(zmq.SUBSCRIBE, "")
    print('\033[31mf01', name)
    while True:
        x = footage_socket.recv_pyobj()
        print('\033[31m',x)
    footage_socket.close()
    context.term()

def f02(name):
    context = zmq.Context()
    footage_socket = context.socket(zmq.SUB)
    footage_socket.bind('tcp://*:9996')
    footage_socket.setsockopt_string(zmq.SUBSCRIBE, "")
    print('\033[32mf02', name)
    while True:
        x = footage_socket.recv_pyobj()
        print('\033[32m',x)
    footage_socket.close()
    context.term()

def f03(name):
    context = zmq.Context()
    footage_socket = context.socket(zmq.SUB)
    footage_socket.bind('tcp://*:9997')
    footage_socket.setsockopt_string(zmq.SUBSCRIBE, "")
    print('\033[33mf03', name)
    while True:
        x = footage_socket.recv_pyobj()
        print('\033[33mf03', x)
    footage_socket.close()
    context.term()

def f04(name):
    context = zmq.Context()
    footage_socket = context.socket(zmq.SUB)
    footage_socket.bind('tcp://*:9998')
    footage_socket.setsockopt_string(zmq.SUBSCRIBE, "")
    print('\033[34mf04', name)
    while True:
        x = footage_socket.recv_pyobj()
        print('\033[34m', x)
    footage_socket.close()
    context.term()

def f05(name):
    context = zmq.Context()
    footage_socket = context.socket(zmq.SUB)
    footage_socket.bind('tcp://*:9999')
    footage_socket.setsockopt_string(zmq.SUBSCRIBE, "")
    print('\033[35mf05', name)
    while True:
        x = footage_socket.recv_pyobj()
        print('\033[35m', x)
    footage_socket.close()
    context.term()

def f06(name):
    context = zmq.Context()
    footage_socket = context.socket(zmq.SUB)
    footage_socket.bind('tcp://*:6101')
    footage_socket.setsockopt_string(zmq.SUBSCRIBE, "")
    print('\033[36mf06', name)
    while True:
        x = footage_socket.recv_pyobj()
        print('\033[36m', x)
    footage_socket.close()
    context.term()

def f07(name):
    context = zmq.Context()
    footage_socket = context.socket(zmq.SUB)
    footage_socket.bind('tcp://*:6102')
    footage_socket.setsockopt_string(zmq.SUBSCRIBE, "")
    print('\033[37mf07', name)
    while True:
        x = footage_socket.recv_pyobj()
        print('\033[37m', x)
    footage_socket.close()
    context.term()

def f08(name):
    context = zmq.Context()
    footage_socket = context.socket(zmq.SUB)
    footage_socket.bind('tcp://*:6103')
    footage_socket.setsockopt_string(zmq.SUBSCRIBE, "")
    print('\033[31mf08', name)
    while True:
        x = footage_socket.recv_pyobj()
        print('\033[31m', x)
    footage_socket.close()
    context.term()

def f09(name):
    context = zmq.Context()
    footage_socket = context.socket(zmq.SUB)
    footage_socket.bind('tcp://*:6104')
    footage_socket.setsockopt_string(zmq.SUBSCRIBE, "")
    print('\033[32mf09', name)
    while True:
        x = footage_socket.recv_pyobj()
        print('\033[32m',x)
    footage_socket.close()
    context.term()

def f10(name):
    context = zmq.Context()
    footage_socket = context.socket(zmq.SUB)
    footage_socket.bind('tcp://*:6105')
    footage_socket.setsockopt_string(zmq.SUBSCRIBE, "")
    print('\033[33mf10', name)
    while True:
        x = footage_socket.recv_pyobj()
        print('\033[33m',x)
    footage_socket.close()
    context.term()

def f11(name):
    context = zmq.Context()
    footage_socket = context.socket(zmq.SUB)
    footage_socket.bind('tcp://*:6106')
    footage_socket.setsockopt_string(zmq.SUBSCRIBE, "")
    print('\033[34mf11', name)
    while True:
        x = footage_socket.recv_pyobj()
        print('\033[34m',x)
    footage_socket.close()
    context.term()

def f12(name):
    context = zmq.Context()
    footage_socket = context.socket(zmq.SUB)
    footage_socket.bind('tcp://*:6107')
    footage_socket.setsockopt_string(zmq.SUBSCRIBE, "")
    print('\033[35mf12', name)
    while True:
        x = footage_socket.recv_pyobj()
        print('\033[35m',x)
    footage_socket.close()
    context.term()

def f13(name):
    context = zmq.Context()
    footage_socket = context.socket(zmq.SUB)
    footage_socket.bind('tcp://*:6108')
    footage_socket.setsockopt_string(zmq.SUBSCRIBE, "")
    print('\033[36mf13', name)
    while True:
        x = footage_socket.recv_pyobj()
        print('\033[36m',x)
    footage_socket.close()
    context.term()

if __name__ == '__main__':
    p01 = Process(target=f01, args=('f01',))
    p01.start()
    p02 = Process(target=f02, args=('f02',))
    p02.start()
    p03 = Process(target=f03, args=('f03',))
    p03.start()
    p04 = Process(target=f04, args=('f04',))
    p04.start()
    p05 = Process(target=f05, args=('f05',))
    p05.start()
    p06 = Process(target=f06, args=('f06',))
    p06.start()
    p07 = Process(target=f07, args=('f07',))
    p07.start()
    p08 = Process(target=f08, args=('f08',))
    p08.start()
    p09 = Process(target=f09, args=('f09',))
    p09.start()
    p10 = Process(target=f10, args=('f10',))
    p10.start()
    p11 = Process(target=f11, args=('f11',))
    p11.start()
    p12 = Process(target=f12, args=('f12',))
    p12.start()
    p13 = Process(target=f13, args=('f13',))
    p13.start()
    p01.join()
    p02.join()
    p03.join()
    p04.join()
    p05.join()
    p06.join()
    p07.join()
    p08.join()
    p09.join()
    p10.join()
    p11.join()
    p12.join()
    p13.join()

