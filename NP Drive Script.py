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
       
       Ch.1 is NOT inverted, while Ch.2 and Ch.3 both are
           Refer to the settings menu on the panel
"""
import json
import socket
import time
import tkinter as tk
from tkinter import ttk
import threading
from tkinter import messagebox
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.ticker import MaxNLocator

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
        
        #Conversion of steps to meters
        self.stepsToMicrons = {1:1, 2:1, 3:1}

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
        tk.Button(self, text="Calibrate", command = self.calibrateAxes).grid(row=5, column=2, pady=8)
        self.stepsBool = tk.Checkbutton(self, text="Go Steps", variable=self.takeSteps, onvalue=1, offvalue=0).grid(row=3, column=4, padx=8, sticky="w")
        
        tk.Button(self, text="Remove pos", command = self.removePos).grid(row = 5, column=1)
        
        # Status label
        self.status = tk.Label(self, text="", anchor="w")
        self.status.grid(row=5, column=0, columnspan=3, sticky="w", padx=4)
        
        #Existing preset GUI
        options = ["Zig Zag"]
        self.dropdown = ttk.Combobox(self, values=options, font=("Arial", 13), width=15)
        self.dropdown.set("Select preset")
        self.dropdown.grid(column=3, row=7, padx=2, pady=5)
        
        self.presetConfirm = tk.Button(self, text="Confirm", command=self.presetConfirm)
        self.presetConfirm.grid(column=4, row=7, padx=2, pady=1, sticky="w")
        
        tk.Label(self, text="Grid Size (µm): ", font=("Arial", 13)).grid(column=3, row=8, sticky="e")
        tk.Label(self, text="Step Size (µm): ", font=("Arial", 13)).grid(column=3, row=9, sticky="e")
        
        self.gridSizeVar = tk.StringVar(value=100)
        self.gridSize = tk.Entry(self, textvariable=self.gridSizeVar, font=("Arial", 13), width=6)
        self.gridSize.grid(column=4, row=8, padx=2, sticky="w")
        
        self.stepSizeVar = tk.StringVar(value=10)
        self.stepSize = tk.Entry(self, textvariable=self.stepSizeVar, font=("Arial", 13), width=6)
        self.stepSize.grid(column=4, row=9, padx=2, sticky="w")
        
        
        #3D Graph position
        self.fig = plt.Figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111, projection="3d")
        self.ax.set_xlabel("X Axis")
        self.ax.set_ylabel("Y Axis")
        self.ax.set_zlabel("Z Axis")
        self.ax.set_title("Platform Path")
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().grid(row=10, column=0, columnspan=5, sticky="nsew", pady = 15)
        
        self.ax.xaxis.set_major_locator(MaxNLocator(nbins=5)) #Set ticks of each axis to a limit of 5 so that graph isn't crowded
        self.ax.yaxis.set_major_locator(MaxNLocator(nbins=5))
        self.ax.zaxis.set_major_locator(MaxNLocator(nbins=5))
        
    def removePos(self):
        positions.clear()
        self.ax.cla()
        self.canvas.draw_idle()
        self.status.config(text="Removed")
    
    def presetConfirm(self):
        val = self.dropdown.get()
        try:
            gridSize = int(self.gridSizeVar.get().strip())
            stepSize = int(self.stepSizeVar.get().strip())
        except:
            messagebox.showwarning("Type Error", "Please enter integer numbers")
            return
        if (val == "Select preset"):
            return
        if (gridSize % stepSize != 0):
            messagebox.showwarning("Invalid input", "Please use divisible step sizes and grid sizes")
            return
        
        funcName = "draw" + val.replace(" ", "")
        func = getattr(self, funcName, None)
        
        if callable(func):
            self.stopped = False
            self.takeSteps.set(1)
            func(stepSize, gridSize)
        else:
            print("Not a function")

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
        
        #Defunct AND debilitated
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
                        command(self.client, {"method": "goStepsReverse", "params": ["3", "0", amp, freq], "jsonrpc": "2.0", "id": 0}) #Prime the 3rd channel because the first move goes in the opposite direction for some reason. Hardware issue most likely
                        command(self.client, {"method": "goStepsReverse",
                                              "params": ["3", f"{z}", amp, freq],
                                              "jsonrpc": "2.0", "id": 0})
                    else:
                        command(self.client, {"method": "setDriveChannel", "params": ["3"], "jsonrpc": "2.0", "id": 0})
                        command(self.client, {"method": "goStepsForward", "params": ["3", "0", amp, freq], "jsonrpc": "2.0", "id": 0}) #Prime the 3rd channel because the first move goes in the opposite direction for some reason. Hardware issue most likely
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
                self.recordPosition(float(getPos(self.client, 1)), float(getPos(self.client, 2)), float(getPos(self.client, 3)))
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

        self.move_btn.config(state=tk.NORMAL)
        self.status.config(text="Stopped")
    
    def recordPosition(self, x, y, z):
        positions.append([x, y, z])
        self.updatePlot()
    
    def updatePlot(self):
        self.ax.cla()
        
        self.ax.set_xlabel("X Axis", labelpad=15)
        self.ax.set_ylabel("Y Axis", labelpad=15)
        self.ax.set_zlabel("Z Axis", labelpad=15)
        
        self.ax.xaxis.set_major_locator(MaxNLocator(nbins=5))
        self.ax.yaxis.set_major_locator(MaxNLocator(nbins=5))
        self.ax.zaxis.set_major_locator(MaxNLocator(nbins=5))
        
        self.ax.xaxis.get_major_formatter().set_useOffset(False)
        self.ax.xaxis.get_major_formatter().set_scientific(False)
        
        self.ax.yaxis.get_major_formatter().set_useOffset(False)
        self.ax.yaxis.get_major_formatter().set_scientific(False)
        
        self.ax.zaxis.get_major_formatter().set_useOffset(False)
        self.ax.zaxis.get_major_formatter().set_scientific(False)
        
        #self.ax.set_zlim(0, 0.01)
        
        
        if positions:
            xs, ys, zs = zip(*positions)
            self.ax.plot(xs, ys, zs, marker='o')
        self.canvas.draw_idle()
    
    def calibrateAxes(self, stepSize=100, reps=10):
        self.status.config(text="Calibrating...")
        totalSteps = stepSize * reps
        print("s")
        self._calibration_axis = 0
        self._calibration_step = 0
        self._calibration_phase = "forward"  # or "backward"
        self._calibration_reps = reps
        self._calibration_stepSize = stepSize
        self._calibration_startPos = None
    
        def start_next_move():
            i = self._calibration_axis
            count = self._calibration_step
            phase = self._calibration_phase
    
            if i >= 3:
                print(self.stepsToMicrons)
                self.status.config(text="Calibration done")
                return
    
            if count == 0:
                self._calibration_startPos = getPos(self.client, i + 1)
    
            # Prepare step values
            moveSteps = [0, 0, 0]
            stepSize = self._calibration_stepSize
            if (i == 2):
                if (phase=="forward"):
                    stepSize *= 10
                if (phase=="backward"):
                    stepSize = int(stepSize * 1.5)
            if phase == "backward":
                stepSize = -stepSize
            moveSteps[i] = stepSize
    
            # Set steps and takeSteps flag
            self.xStepsVar.set(str(moveSteps[0]))
            self.yStepsVar.set(str(moveSteps[1]))
            self.zStepsVar.set(str(moveSteps[2]))
            self.takeSteps.set(1)
    
            # Launch move
            self.move_to_inputs()
            # Now wait for finishMove() to call back to continue
    
        def finish_callback(ok):
            # Called by finishMove after each move finishes
            if not ok:
                self.status.config(text="Calibration error")
                return
    
            count = self._calibration_step + 1
            i = self._calibration_axis
            phase = self._calibration_phase
    
            if count >= self._calibration_reps:
                if phase == "forward":
                    # Switch to backward moves
                    self._calibration_phase = "backward"
                    self._calibration_step = 0
                    start_next_move()
                else:
                    # Backward phase done, calculate result and move on axis
                    endPos = getPos(self.client, i + 1)
                    distMoved = abs(endPos - self._calibration_startPos)
                    sPM = (self._calibration_stepSize * self._calibration_reps) / (distMoved * 1e6) if distMoved != 0 else 0
                    self.stepsToMicrons[i + 1] = sPM
                    self._calibration_axis += 1
                    self._calibration_phase = "forward"
                    self._calibration_step = 0
                    start_next_move()
            else:
                self._calibration_step = count
                start_next_move()
    
        # Override your finishMove to chain calibration steps
        old_finishMove = self.finishMove
        def new_finishMove(ok):
            finish_callback(ok)
            old_finishMove(ok)
        self.finishMove = new_finishMove
    
        # Start first move
        start_next_move()




    
    
    def drawZigZag(self, stepSize, gridSize, row=0, step=0, direction=1):
        if self.stopped:
            self.status.config(text="Zigzag stopped")
            return
    
        if row >= gridSize:
            self.status.config(text="Zigzag complete")
            return
    
        if step < gridSize:
            # Move along X axis
            self.xStepsVar.set(int(stepSize * self.stepsToMicrons[1] * direction))
            self.yStepsVar.set(0)
            self.zStepsVar.set(0)
            self.move_to_inputs()
            
            # Schedule next step after a delay (adjust delay as needed)
            self.after(1000, lambda: self.drawZigZag(stepSize, gridSize, row, step + stepSize, direction))
        else:
            # Move down one step in Z axis and switch direction
            self.xStepsVar.set(0)
            self.yStepsVar.set(int(stepSize * self.stepsToMicrons[2]))
            self.zStepsVar.set(int(stepSize * self.stepsToMicrons[3]))
            self.move_to_inputs()
    
            # Start next row, reverse direction
            self.after(1000, lambda: self.drawZigZag(stepSize, gridSize, row + stepSize, 0, -direction))


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
        response = client.recv(1024)
    
    except socket.error:
        print("Failed to send data")
    
    response_json = json.loads(response)
    return response_json

def waitMovement(client, channel, target, tolerance = 0.00001, timeout = 10, interval = 0.05): #Debilitated
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
    
