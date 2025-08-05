# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.

Channel - Which to move
Amplitude - Equivalent to how large the steps will be
Frequency - Equivalent to the speed of the movement

Notes: From a side-view
       Ch.1 goes towards and away from you (x-axis)
       Ch.2 goes left and right (z-axis)
       Ch.3 goes up and down (y-axis)
       
       Model: B100
"""
import json
import socket
import time

def getPos(client, channel):
    resp = command(client, {"method": "getPosition",
                     "params": [str(channel)],
                     "jsonrpc": "2.0",
                     "id": 0
                     })
    return resp["result"]

def command(client, rpc):
    rpc_bytes = json.dumps(rpc).encode("utf-8")
    try:
        client.send(rpc_bytes)
        response = client.recv(128)
    
    except socket.error:
        print("Failed to send data")
    
    response_json = json.loads(response)
    return response_json

def waitMovement(client, channel, target, tolerance = 0.00005, timeout = 10, interval = 0.05):
    start = time.time()
    while time.time() - start < timeout:
        resp = command(client, {"method": "getPosition",
                         "params": [str(channel)],
                         "jsonrpc": "2.0",
                         "id": 0
                         })
        status = resp["result"]
        if (abs(target - status) <= tolerance):
            print("Movement complete")
            return True
        time.sleep(interval)
    print("Timed Out")
    return False

def main():
    IP = "192.168.0.100"
    PORT = 6002
    
    #Connection
    try:
        connect = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error:
        print("Failed to create socket")
    
    connect.connect((IP, PORT))
    print("Socket has been connected to", IP)
    
    #goToOriginalPosition(connect)
    traceSquare(connect)
    
    rpc = {
        "method": "getPosition",
        "params": ["1"],
        "jsonrpc": "2.0",
        "id": 0,
        }
    resp = command(connect, rpc)
    print("Return value: " + str(resp["result"]) + " micrometers")
    rpc = {
        "method": "getPosition",
        "params": ["2"],
        "jsonrpc": "2.0",
        "id": 0,
        }
    resp = command(connect, rpc)
    print("Return value: " + str(resp["result"]) + " micrometers")
    rpc = {
        "method": "getPosition",
        "params": ["3"],
        "jsonrpc": "2.0",
        "id": 0,
        }
    resp = command(connect, rpc)
    print("Return value: " + str(resp["result"]) + " micrometers")
        
def goToOriginalPosition(client):
    #Establish a setStopLimit
    rpc = {"method": "setStopLimit",
           "params": ["1", "0.00001"],
           "jsonrpc": "2.0",
           "id": 0}
    resp = command(client, rpc)
    rpc = {"method": "setStopLimit",
           "params": ["2", "0.00001"],
           "jsonrpc": "2.0",
           "id": 0}
    resp = command(client, rpc)
    rpc = {"method": "setStopLimit",
           "params": ["3", "0.00001"],
           "jsonrpc": "2.0",
           "id": 0}
    resp = command(client, rpc)
    
    #Activate Channel 1 relay
    rpc = {"method": "setDriveChannel",
           "params": ["1"],
           "jsonrpc": "2.0",
           "id": 0}
    resp = command(client, rpc)
    rpc = {"method": "goPosition",
           "params": ["1", "0.001270845668667555", "300", "1500"],
           "jsonrpc": "2.0",
           "id": 0}
    resp = command(client, rpc)
    waitMovement(client, 1, 0.001270845668667555)
    
    #Activate Channel 2 relay
    rpc = {"method": "setDriveChannel",
           "params": ["2"],
           "jsonrpc": "2.0",
           "id": 0}
    resp = command(client, rpc)
    rpc = {"method": "goPosition",
           "params": ["2", "0.0017568406247109166", "300", "1500"],
           "jsonrpc": "2.0",
           "id": 0}
    resp = command(client, rpc)
    waitMovement(client, 2, 0.0017568406247109166)

    
    #Activate Channel 3 relay
    rpc = {"method": "setDriveChannel",
           "params": ["3"],
           "jsonrpc": "2.0",
           "id": 0}
    resp = command(client, rpc)
    rpc = {"method": "goPosition",
           "params": ["3", "0.003075189428376382", "300", "1500"],
           "jsonrpc": "2.0",
           "id": 0}
    resp = command(client, rpc)
    waitMovement(client, 3, 0.003075189428376382)

def traceSquare(client):
    command(client, {"method": "goInterval",
                     "params": ["3", "0.0001", "300", "1500"],
                     "jsonrpc": "2.0", 
                     "id": 0})
    root = getPos(client, 3)
    waitMovement(client, 3, root + 0.0001)
    
    command(client, {"method": "goInterval",
                     "params": ["2", "0.0005", "300", "1500"],
                     "jsonrpc": "2.0", 
                     "id": 0})
    root = getPos(client, 2)
    waitMovement(client, 2, root + 0.0005)
    
    command(client, {"method": "goInterval",
                     "params": ["3", "-0.0001", "300", "1500"],
                     "jsonrpc": "2.0", 
                     "id": 0})
    root = getPos(client, 3)
    waitMovement(client, 3, root - 0.0001)
    
    command(client, {"method": "goInterval",
                     "params": ["2", "-0.0005", "300", "1500"],
                     "jsonrpc": "2.0", 
                     "id": 0})
    root = getPos(client, 2)
    waitMovement(client, 2, root - 0.0005)
    



if __name__ == "__main__":
    main()
    
