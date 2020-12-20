import zmq
import sys
import json
import pdb
import argparse


masterurl_default = 'tcp://master:5551'
slaveurl_default = 'tcp://slave:5552'

def parse_args():
    """ Parses command line arguments
    Returns:
        dict: all keyword arguments passed from the command line
    """
    parser = argparse.ArgumentParser(description='Bioelectronica Hypercell '
        'client commands')

    parser.add_argument('command', type=str, 
            help='Available commands are start, stop, json, roi, leakdown')
    
    parser.add_argument('params', type=str, nargs='*', help='command parameters')
    parser.add_argument('-m', '--masterurl', type=str, default=masterurl_default, 
            help='URL of master device')

    parser.add_argument('-s', '--slaveurl', type=str, default=slaveurl_default,
            help='URL of slave device')

    args = parser.parse_args()
    return vars(args)


def client(command, params = None, masterurl=masterurl_default, 
        slaveurl=slaveurl_default):
    """ Executes a hypercell command from the client. 
        Given a command, this function will send it to the instrument on either
        the master or slave address. 

        Parameters are described in the parse_args function

    """
    
    print('Executing command {} with params {} on\nMaster: {}\nSlave: {}'
            .format(command, params, masterurl, slaveurl))
    

    '''
    if len(sys.argv) < 2:
        print("No arguments given!")
        sys.exit()
    elif len(sys.argv) < 3:
        ia = [sys.argv[-1]]
    else:
        ia = list(sys.argv[1:])
    '''

    c1 = zmq.Context()
    s1 = c1.socket(zmq.REQ)
    s1.connect(masterurl)

    c2 = zmq.Context()
    s2 = c2.socket(zmq.REQ)
    s2.connect(slaveurl)
   
    if command=='json':
        # Command format
        # json <instrument_json_filename_to_update> <updated_settings_json>
        with open(param[1],'r') as f:
            js=json.load(f)
        ia=[command,param[0],js]
    elif command=='hello':
        ia=[command]
    else:
        print('Invalid command')
        return;
    #s1.send_pyobj(ia)
    s2.send_pyobj(ia)
    
    print("Sending...")
    #msg=s1.recv_string()
    msg2=s2.recv_string()
    #print(msg)
    print(msg2)
 

def main():
    kwargs = parse_args()
    client(**kwargs)

if __name__ == "__main__":
    main()

   
