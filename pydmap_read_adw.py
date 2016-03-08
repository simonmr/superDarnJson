# script for reading in dmap strings over a socket into a dictionary
# 7/1/2015
# jon klein, jtklein@alaska.edu

import numpy as np
import pdb
import socket 
import time
import json
import datetime
import time
import signal

DATACODE = 33
DATACHAR = 1
DATASHORT = 2
DATAINT = 3
DATAFLOAT = 4
DATADOUBLE = 8
DATASTRING = 9
DATALONG = 10
DATAUCHAR = 16
DATAUSHORT = 17
DATAUINT = 18
DATAULONG = 19
DATAMAP = 255
NULL = chr(0)

DTYPE_CODES = { \
    DATACHAR:np.uint8,\
    DATASHORT:np.int16,\
    DATAINT:np.int32,\
    DATAFLOAT:np.float32,\
    DATASTRING:str}

TIMEOUT = datetime.timedelta(seconds = 60)
RESTART_DELAY = 5

def recv_dtype(sock, dtype, nitems = 1):
    if dtype == str:
        return recv_str(sock)
    
    dstr = ''
    while len(dstr) < dtype().nbytes * nitems:
        dstr += sock.recv(1)

    data = np.fromstring(dstr, dtype=dtype, count=nitems)
    if nitems == 1:
        return data[0]
    return data

def recv_str(sock):
    dstr = ''
    c = sock.recv(1)

    while c != NULL:
        dstr += c
        c = sock.recv(1)
    return dstr

def readPacket(sock):
    timeout = False
    scalars = {}
    vectors = {}

    # read in header
    datacode = recv_dtype(sock, np.int32)

    # this isn't very robust.. try to find header.. or something that looks like header
    starttime = datetime.datetime.now()
    
    while datacode != 65537:
        print 'looking for header..'
        datacode = recv_dtype(sock, np.int32)

        if (starttime - datetime.datetime.now()) > TIMEOUT:
            timeout = True
            break
    
    if not timeout:
        sze = recv_dtype(sock, np.int32)
        snum = recv_dtype(sock, np.int32)
        anum = recv_dtype(sock, np.int32)

        # read in scalars
        for s in range(snum):
            try:
                name = recv_str(sock)
                dtype = DTYPE_CODES[recv_dtype(sock, np.uint8)]
                payload = recv_dtype(sock, dtype)
                scalars[name] = payload
            except KeyError:
                print('Unsupported data type, skipping the rest of the entry')
                timeout = True
                break

        # read in vectors
        for a in range(anum):
            name = recv_str(sock)
            try:
                dtype = DTYPE_CODES[recv_dtype(sock, np.uint8)]
            except KeyError:
                print('Unsupported data type, skipping the rest of the entry')
                timeout = True
                break
            ndims = recv_dtype(sock, np.int32)
            dims = recv_dtype(sock, np.int32, ndims)
            payload = recv_dtype(sock, dtype, np.prod(dims))
            if ndims > 1:
                payload = np.reshape(payload, tuple(dims[::-1]))
            vectors[name] = payload
    
    return scalars, vectors, timeout

def createjson(scalars, vectors):
    json_payload = {}

    for scalar in scalars.keys():
        payload = scalars[scalar]
        if isinstance(payload, str):
            json_payload[scalar] = payload
        else:
            json_payload[scalar] = np.asscalar(payload)

    for vector in vectors.keys():
        payload = vectors[vector]
        # convert numpy array to list, recursively traverse and convert to jsonable data type..
        payload = payload.tolist()
        json_payload[vector] = payload
    return json.dumps(json_payload)


def main():
    HOST = 'superdarn.gi.alaska.edu'
    PORT = 6032
    timeout = False
    PORT_JSON_SERVE = 6042
    
    s = None
    s_json = None
    json_conn = None
    while True:
        try:
			s_json = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s_json.bind(('', PORT_JSON_SERVE))
			s_json.listen(10)
			s_json.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
			print('waiting for connection..')
			json_conn, json_addr = s_json.accept()
			print('connected!')
			while True:
				s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				s.connect((HOST, PORT))
				s.settimeout(30.0)
				while not timeout:
					scalars, vectors, timeout = readPacket(s)
					json_str = createjson(scalars, vectors)
					print json_str
					json_conn.send(json_str)
				if timeout:
					break
				print('timed out on dmap feed, restarting server')
				s.close() 
				time.sleep(RESTART_DELAY)
        
        except:
            print('crashed, restarting server')
            if s_json:
                s_json.close()
            if s:
                s.close()
            if json_conn:
                json_conn.close()
            time.sleep(15)
            
            




if __name__ == '__main__':
    main()
