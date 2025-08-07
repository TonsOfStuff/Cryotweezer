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
import tkinter as tk
from tkinter import ttk
import threading

import threading
import tkinter as tk
from tkinter import messagebox

amp = "100"   #amplitude param
freq  = "1500"  #frequency param

positions = []

class Page(tk.Frame):
    def __init__(self, parent, client):
        super().__init__(parent)
        self.client = client

        # Editable StringVars
        self.x_var = tk.StringVar(value="")
        self.y_var = tk.StringVar(value="")
        self.z_var = tk.StringVar(value="")
        
        self.xStepsVar = tk.StringVar(value="")
        self.yStepsVar = tk.StringVar(value="")
        self.zStepsVar = tk.StringVar(value="")
        
        self.ampVar = tk.StringVar(value=amp)
        self.freqVar = tk.StringVar(value=freq)
        
        #Checkbutton
        self.takeSteps = tk.IntVar()
        
        #Stop check var
        self.stopped = False

        # Labels
        tk.Label(self, text="Go to:", font=("Arial", 18), padx=8).grid(row=0, column=1, sticky="w")
        tk.Label(self, text="Steps:", font=("Arial", 18), padx=8).grid(row=0, column=2, sticky="w")
        tk.Label(self, text="Misc:", font=("Arial", 18), padx=8).grid(row=0, column=4, sticky="w")
        
        tk.Label(self, text="X:", font=("Arial", 16), padx=8).grid(row=1, column=0, sticky="e")
        tk.Label(self, text="Y:", font=("Arial", 16), padx=8).grid(row=2, column=0, sticky="e")
        tk.Label(self, text="Z:", font=("Arial", 16), padx=8).grid(row=3, column=0, sticky="e")
        
        tk.Label(self, text="Amp:", font=("Arial", 16), padx=8).grid(row=1, column=3, stick="e")
        tk.Label(self, text="Freq:", font=("Arial", 16), padx=8).grid(row=2, column=3, stick="e")

        # Editable Entry widgets
        self.x_entry = tk.Entry(self, textvariable=self.x_var, font=("Arial", 16), width=14)
        self.y_entry = tk.Entry(self, textvariable=self.y_var, font=("Arial", 16), width=14)
        self.z_entry = tk.Entry(self, textvariable=self.z_var, font=("Arial", 16), width=14)
        self.x_entry.grid(row=1, column=1, padx=6, pady=4, sticky="w")
        self.y_entry.grid(row=2, column=1, padx=6, pady=4, sticky="w")
        self.z_entry.grid(row=3, column=1, padx=6, pady=4, sticky="w")
        
        self.xSteps = tk.Entry(self, textvariable=self.xStepsVar, font=("Arial", 16), width=14)
        self.ySteps = tk.Entry(self, textvariable=self.yStepsVar, font=("Arial", 16), width=14)
        self.zSteps = tk.Entry(self, textvariable=self.zStepsVar, font=("Arial", 16), width=14)
        self.xSteps.grid(row=1, column=2, padx=6, pady=4, sticky="w")
        self.ySteps.grid(row=2, column=2, padx=6, pady=4, sticky="w")
        self.zSteps.grid(row=3, column=2, padx=6, pady=4, sticky="w")
        
        self.ampEntry = tk.Entry(self, textvariable=self.ampVar, font=("Arial", 16), width=8).grid(row=1, column=4, padx=8)
        self.freqEntry = tk.Entry(self, textvariable=self.freqVar, font=("Arial", 16), width=8).grid(row=2, column=4, padx=8)

        # Buttons
        tk.Button(self, text="Read Current", command=self.read_current, width=11).grid(row=4, column=1, pady=8)
        self.move_btn = tk.Button(self, text="Move to XYZ", command=self.move_to_inputs)
        self.move_btn.grid(row=4, column=2, pady=8)
        
        tk.Button(self, text="Stop Motion", command = self.stopMove).grid(row = 4, column=3, padx=8)
        
        self.stepsBool = tk.Checkbutton(self, text="Go Steps", variable=self.takeSteps, onvalue=1, offvalue=0).grid(row=3, column=4, padx=8, sticky="w")

        # Status label
        self.status = tk.Label(self, text="", anchor="w")
        self.status.grid(row=5, column=0, columnspan=3, sticky="w", padx=4)

    def read_current(self):
        """Populate entries with current machine positions (channels 1–3)."""
        try:
            x = getPos(self.client, 1)
            y = getPos(self.client, 2)
            z = getPos(self.client, 3)
            self.x_var.set(f"{x:.10f}")
            self.y_var.set(f"{y:.10f}")
            self.z_var.set(f"{z:.10f}")
            self.status.config(text="Read current positions")
        except Exception as e:
            messagebox.showerror("Read error", str(e))

    def move_to_inputs(self):
        """Kick off a background move using the values from the entries."""
        self.stopped = False
        try:
            if (self.takeSteps.get() == 0):
                #Get the entered values of x, y, z
                tempX = self.x_var.get().strip()
                tempY = self.y_var.get().strip()
                tempZ = self.z_var.get().strip()
                if (tempX == ""):
                    tempX = getPos(self.client, 1)
                if (tempY == ""):
                    tempY = getPos(self.client, 2)
                if (tempZ == ""):
                    tempZ = getPos(self.client, 3)
                
                x_tgt = float(tempX)
                y_tgt = float(tempY)
                z_tgt = float(tempZ)

            #Get entered steps for x, y, z
            tempX = self.xStepsVar.get().strip()
            tempY = self.yStepsVar.get().strip()
            tempZ = self.zStepsVar.get().strip()
            if (tempX == ""):
                tempX = 0
            if (tempY == ""):
                tempY = 0
            if (tempZ == ""):
                tempZ = 0
            
            xStep = int(tempX)
            yStep = int(tempY)
            zStep = int(tempZ)
            
            #Get the amplitude and frequency from the amp and freq textbok
            amp = float(self.ampVar.get().strip())
            freq = float(self.freqVar.get().strip())
        except ValueError:
            messagebox.showwarning("Invalid input", "Please enter numeric X, Y, Z values.")
            return

        # Disable the button during motion
        self.move_btn.config(state=tk.DISABLED)
        self.status.config(text="Moving...")

        def goToPos():
            ok = True
            command(self.client, {"method": "setStopLimit", "params": ["1", "0.000001"], "jsonrpc": "2.0", "id": 0})
            command(self.client, {"method": "setStopLimit", "params": ["2", "0.000001"], "jsonrpc": "2.0", "id": 0})
            command(self.client, {"method": "setStopLimit", "params": ["3", "0.000001"], "jsonrpc": "2.0", "id": 0})
            
            try:
                print
                # Move X (channel 1)
                command(self.client, {"method": "setDriveChannel", "params": ["1"], "jsonrpc": "2.0", "id": 0})
                command(self.client, {"method": "goPosition",
                                      "params": ["1", f"{x_tgt}", amp, freq],
                                      "jsonrpc": "2.0", "id": 0})
                ok = ok and waitMovement(self.client, 1, x_tgt)

                # Move Y (channel 2)
                command(self.client, {"method": "setDriveChannel", "params": ["2"], "jsonrpc": "2.0", "id": 0})
                command(self.client, {"method": "goPosition",
                                      "params": ["2", f"{y_tgt}", amp, freq],
                                      "jsonrpc": "2.0", "id": 0})
                ok = ok and waitMovement(self.client, 2, y_tgt)

                # Move Z (channel 3)
                command(self.client, {"method": "setDriveChannel", "params": ["3"], "jsonrpc": "2.0", "id": 0})
                command(self.client, {"method": "goPosition",
                                      "params": ["3", f"{z_tgt}", amp, freq],
                                      "jsonrpc": "2.0", "id": 0})
                ok = ok and waitMovement(self.client, 3, z_tgt)

            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Move error", str(e)))
                ok = False
            finally:
                positions.append([x_tgt, y_tgt, z_tgt])
                self.after(0, lambda: self.finishMove(ok))
        
        def goSteps(xStep, yStep, zStep, goTo = False, xTar = 0, yTar = 0, zTar = 0, cX = False, cY = False, cZ = False):
            ok = False
            if (goTo == True):
                if (xTar > getPos(self.client, 1) and xStep < 0):
                    xStep = -xStep
                if (xTar < getPos(self.client, 1) and xStep > 0):
                    xStep = -xStep
                if (yTar > getPos(self.client, 2) and yStep < 0):
                    yStep = -yStep
                if (yTar < getPos(self.client, 2) and yStep > 0):
                    yStep = -yStep
                if (zTar > getPos(self.client, 3) and zStep < 0):
                    zStep = -zStep
                if (zTar < getPos(self.client, 3) and zStep > 0):
                    zStep = -zStep
                    
                #Check if axis movement is complete
                if (cX == True):
                    xStep = 0
                if (cY == True):
                    yStep = 0
                if (cZ == True):
                    zStep = 0
            try:
                # Move X (channel 1) if need to, x is reversed so reverse increases coord
                if (xStep != 0):
                    if (xStep < 0):
                        x = abs(xStep)
                        command(self.client, {"method": "setDriveChannel", "params": ["1"], "jsonrpc": "2.0", "id": 0})
                        command(self.client, {"method": "goStepsForward",
                                              "params": ["1", f"{x}", amp, freq],
                                              "jsonrpc": "2.0", "id": 0})
                    else:
                        command(self.client, {"method": "setDriveChannel", "params": ["1"], "jsonrpc": "2.0", "id": 0})
                        command(self.client, {"method": "goStepsReverse",
                                              "params": ["1", f"{xStep}", amp, freq],
                                              "jsonrpc": "2.0", "id": 0})
                    time.sleep(abs(xStep) / freq + 0.2)


                # Move Y (channel 2)
                if (yStep != 0):
                    if(yStep < 0):
                        y = abs(yStep)
                        command(self.client, {"method": "setDriveChannel", "params": ["2"], "jsonrpc": "2.0", "id": 0})
                        command(self.client, {"method": "goStepsReverse",
                                              "params": ["2", f"{y}", amp, freq],
                                              "jsonrpc": "2.0", "id": 0})
                    else:
                        command(self.client, {"method": "setDriveChannel", "params": ["2"], "jsonrpc": "2.0", "id": 0})
                        command(self.client, {"method": "goStepsForward",
                                              "params": ["2", f"{yStep}", amp, freq],
                                              "jsonrpc": "2.0", "id": 0})
                    time.sleep(abs(yStep) / freq + 0.2)

                # Move Z (channel 3)
                if (zStep != 0):
                    if (zStep < 0):
                        z = abs(zStep)
                        command(self.client, {"method": "setDriveChannel", "params": ["3"], "jsonrpc": "2.0", "id": 0})
                        command(self.client, {"method": "goStepsReverse",
                                              "params": ["3", f"{z}", amp, freq],
                                              "jsonrpc": "2.0", "id": 0})
                    else:
                        command(self.client, {"method": "setDriveChannel", "params": ["3"], "jsonrpc": "2.0", "id": 0})
                        command(self.client, {"method": "goStepsForward",
                                              "params": ["3", f"{zStep}", amp, freq],
                                              "jsonrpc": "2.0", "id": 0})
                    time.sleep(abs(zStep) / freq + 0.2)
                ok = True

            except Exception as e:
                print(e)
                self.after(0, lambda: messagebox.showerror("Move error"))
                ok = False
            finally:
                positions.append([float(getPos(self.client, 1)), float(getPos(self.client, 2)), float(getPos(self.client, 3))])
                if (goTo == False):
                    self.after(0, lambda: self.finishMove(ok))
        
        def refinedGoTo():
            xComplete = False
            yComplete = False
            zComplete = False
            
            tolerance = 0.0000015
            for i in range(100):
                if (self.stopped == True):
                    break
                
                goSteps(xStep, yStep, zStep, True, x_tgt, y_tgt, z_tgt, xComplete, yComplete, zComplete)
                if (abs(getPos(self.client, 1) - x_tgt) < tolerance and xComplete == False):
                    print("x complete")
                    xComplete = True
                if (abs(getPos(self.client, 2) - y_tgt) < tolerance and yComplete == False):
                    print("y complete")
                    yComplete = True
                if (abs(getPos(self.client, 3) - z_tgt) < tolerance and zComplete == False):
                    print("z complete")
                    zComplete = True
                
                if (xComplete and yComplete and zComplete):
                    print("Complete")
                    self.after(0, lambda: self.finishMove(True))
                    return
            
            if (self.stopped != True):
                self.after(0, lambda: self.finishMove(False))
                
        
        #Take steps is checked, use the steps command
        if (self.takeSteps.get() == 1):
            threading.Thread(target=goSteps, args=(xStep, yStep, zStep), daemon=True).start()
        else:
            threading.Thread(target=refinedGoTo, daemon=True).start()

    def finishMove(self, ok: bool):
        """Re-enable UI and update status after move completes."""
        self.move_btn.config(state=tk.NORMAL)
        self.status.config(text="Move complete." if ok else "Move finished with errors.")
    
    def stopMove(self):
        self.stopped = True
        check = command(self.client, {"method": "stopMotion", "params": [], "jsonrpc": "2.0", "id": 0})
        print(check["result"])
        self.move_btn.config(state=tk.NORMAL)
        self.status.config(text="Stopped")



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

def waitMovement(client, channel, target, tolerance = 0.00001, timeout = 10, interval = 0.05):
    start = time.time()
    while time.time() - start < timeout:
        resp = command(client, {"method": "getStatusPositioning", "params": [], "jsonrpc": "2.0", "id": 0})
        if not resp["result"]:
            print("Positioning finished")
            return True
        time.sleep(interval)
    print("Timed Out")
    return False


        
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



def initWindow(client): #Tkinter Winodw Set-up
    root = tk.Tk()
    root.title("Live XYZ Position")
    page = Page(root, client)
    page.pack(padx=12, pady=12)
    # Ensure socket closes on window close
    def _on_close():
        try:
            client.close()
        except Exception:
            pass
        root.destroy()
    root.protocol("WM_DELETE_WINDOW", _on_close)
    root.mainloop()

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

    initWindow(connect)
    
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

if __name__ == "__main__":
    #try:
        main()
    #except:
        #print("Program closed")
    
