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

amp = "300"   #amplitude param
freq  = "1500"  #frequency param

class Page(tk.Frame):
    def __init__(self, parent, client):
        super().__init__(parent)
        self.client = client

        # Editable StringVars
        self.x_var = tk.StringVar(value="")
        self.y_var = tk.StringVar(value="")
        self.z_var = tk.StringVar(value="")

        # Labels
        tk.Label(self, text="X:", font=("Arial", 16), padx=8).grid(row=0, column=0, sticky="e")
        tk.Label(self, text="Y:", font=("Arial", 16), padx=8).grid(row=1, column=0, sticky="e")
        tk.Label(self, text="Z:", font=("Arial", 16), padx=8).grid(row=2, column=0, sticky="e")

        # Editable Entry widgets
        self.x_entry = tk.Entry(self, textvariable=self.x_var, font=("Arial", 16), width=14)
        self.y_entry = tk.Entry(self, textvariable=self.y_var, font=("Arial", 16), width=14)
        self.z_entry = tk.Entry(self, textvariable=self.z_var, font=("Arial", 16), width=14)
        self.x_entry.grid(row=0, column=1, padx=6, pady=4, sticky="w")
        self.y_entry.grid(row=1, column=1, padx=6, pady=4, sticky="w")
        self.z_entry.grid(row=2, column=1, padx=6, pady=4, sticky="w")

        # Buttons
        tk.Button(self, text="Read Current", command=self.read_current).grid(row=3, column=0, pady=8, sticky="e")
        self.move_btn = tk.Button(self, text="Move to XYZ", command=self.move_to_inputs)
        self.move_btn.grid(row=3, column=1, pady=8, sticky="w")

        # Optional: status label
        self.status = tk.Label(self, text="", anchor="w")
        self.status.grid(row=4, column=0, columnspan=2, sticky="w", padx=4)

    def read_current(self):
        """Populate entries with current machine positions (channels 1–3)."""
        try:
            x = getPos(self.client, 1)
            y = getPos(self.client, 2)
            z = getPos(self.client, 3)
            self.x_var.set(f"{x:.6f}")
            self.y_var.set(f"{y:.6f}")
            self.z_var.set(f"{z:.6f}")
            self.status.config(text="Read current positions.")
        except Exception as e:
            messagebox.showerror("Read error", str(e))

    def move_to_inputs(self):
        """Kick off a background move using the values from the entries."""
        try:
            x_tgt = float(self.x_var.get().strip())
            y_tgt = float(self.y_var.get().strip())
            z_tgt = float(self.z_var.get().strip())
        except ValueError:
            messagebox.showwarning("Invalid input", "Please enter numeric X, Y, Z values.")
            return

        # Disable the button during motion
        self.move_btn.config(state=tk.DISABLED)
        self.status.config(text="Moving...")

        def _worker():
            ok = True
            try:
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
                self.after(0, lambda: self._finish_move(ok))

        threading.Thread(target=_worker, daemon=True).start()

    def _finish_move(self, ok: bool):
        """Re-enable UI and update status after move completes."""
        self.move_btn.config(state=tk.NORMAL)
        self.status.config(text="Move complete." if ok else "Move finished with errors.")



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
    #traceSquare(connect)
    
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
    try:
        main()
    except:
        print("Program closed")
    