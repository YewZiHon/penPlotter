# import the necessary packages
from __future__ import print_function
from PIL import Image
from PIL import ImageTk
import tkinter
import threading
import datetime
import cv2
import os
import sys
import enum
import potrace
from svg_to_gcode.svg_parser import parse_file
from svg_to_gcode.compiler import Compiler, interfaces
import time
import serial
import glob


state = enum.Enum('state', ['takePhoto', 'previewPhoto', 'gen', 'plot', 'paused'])

if not os.path.isdir(sys.path[0]+"\\temp"):
    os.makedirs(sys.path[0]+"\\temp")
if not os.path.isdir(sys.path[0]+"\\temp\\img"):
    os.makedirs(sys.path[0]+"\\temp\\img")
if not os.path.isdir(sys.path[0]+"\\temp\\dot"):
    os.makedirs(sys.path[0]+"\\temp\\dot")
if not os.path.isdir(sys.path[0]+"\\temp\\gcode"):
    os.makedirs(sys.path[0]+"\\temp\\gcode")

class plotter:
    def __init__(self, vs):
# store the video stream object and output path, then initialize
# the most recently read frame, thread for reading frames, and
# the thread stop event
        self.vs = vs
        self.frame = None
        self.thread = None
        self.state=state.takePhoto
        # initialize the root window and image panel
        self.root = tkinter.Tk()              
        self.root.state('zoomed')
        self.root.configure(bg='light sky blue')

        self.panel = tkinter.Label()
        self.btn0=tkinter.Button(self.root)
        self.btn1=tkinter.Button(self.root)
        self.btn2=tkinter.Button(self.root)

        self.panel.pack(side=tkinter.TOP, padx=10, pady=10)

        self.startStream()

        self.root.wm_title("Plotter")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def startStream(self,_=None):
        self.root.bind('<Escape>', None)
        self.btn1.pack_forget()
        self.btn2.pack_forget()
        self.state=state.takePhoto
        self.btn0 = tkinter.Button(self.root, text="Take A Photo (Space)",command=self.takeSnapshot)
        self.btn0.pack(anchor=tkinter.S)
        self.root.bind('<space>', self.spaceHandle)

        self.thread = threading.Thread(target=self.videoLoop, args=(), daemon=True)
        self.thread.start()

    def videoLoop(self):
        while self.state==state.takePhoto:
            
            _, self.frame = self.vs.read()
            maxwidth, maxheight = 1600, 800
            f1 = maxwidth / self.frame.shape[1]
            f2 = maxheight / self.frame.shape[0]
            f = min(f1, f2)  # resizing factor
            dim = (int(self.frame.shape[1] * f), int(self.frame.shape[0] * f))
            self.frame = cv2.resize(self.frame, dim)

            image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(image)
            image = ImageTk.PhotoImage(image)
            
            self.panel.configure(image=image)
            self.panel.image = image

    def spaceHandle(self,_):

        self.takeSnapshot()

    def takeSnapshot(self):
        self.root.bind('<space>', None)
        self.filename = datetime.datetime.now().strftime("%dd%mm%Yy-%Hh%Mn%Ss")
        # save the file
        print("saving",sys.path[0]+"\\temp\\img\\"+self.filename+".jpeg")
        print(cv2.imwrite(sys.path[0]+"\\temp\\img\\"+self.filename+".jpeg", self.frame))
        self.state=state.previewPhoto
        self.btn0.pack_forget()
        self.btn1 = tkinter.Button(self.root, text="Back(Esc)",command=self.startStream)
        self.btn1.pack(anchor=tkinter.SW, padx=10,pady=10)
        print("bind1")
        self.btn2 = tkinter.Button(self.root, text="Continue(Space)",command=self.genGcode)
        self.btn2.pack(anchor=tkinter.SE, padx=10,pady=10)
        self.root.bind('<Escape>', self.startStream)
        print("bind2")
        self.root.bind('<space>', self.genGcode)
        self.root.update()
        self.root.update_idletasks()
    
    def preprocess(self):
        image=cv2.imread(sys.path[0]+"\\temp\\img\\"+self.filename+".jpeg")
        image=cv2.Canny(image,1,50)

        image = image[0:800, 133:933]
        cv2.imwrite(sys.path[0]+"\\temp\\img\\"+self.filename+"canny.jpeg",image)

        return

    def genGcode(self,_=None):
        if self.state ==state.gen:
            return
        self.state=state.gen
        self.root.bind('<Escape>', None)
        self.root.bind('<space>', None)
        self.btn1.pack_forget()
        self.btn2.pack_forget()
        self.btn1.update_idletasks()
        self.btn2.update_idletasks()

        print("Gcode")

        self.preprocess()

        image = Image.open(sys.path[0]+"\\temp\\img\\"+self.filename+"canny.jpeg")

        generating = Image.fromarray(cv2.imread(sys.path[0]+"\\generating.jpg"))
        generating = ImageTk.PhotoImage(generating)
        
        self.panel.configure(image=generating)
        self.panel.image = generating
        self.panel.update_idletasks()

        bm = potrace.Bitmap(image)
        # bm.invert()
        plist = bm.trace(
            turdsize=0,
            turnpolicy=potrace.POTRACE_TURNPOLICY_MINORITY,
            alphamax=0.8,
            opticurve=True,
            opttolerance=0.1,
        )
        with open(sys.path[0]+"\\temp\\img\\"+self.filename+".svg", "w") as fp:
            fp.write(
                f'''<svg version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{image.width}" height="{image.height}" viewBox="0 0 {image.width} {image.height}">''')
            parts = []
            for curve in plist:
                fs = curve.start_point
                parts.append(f"M{fs.x},{fs.y}")
                for segment in curve.segments:
                    if segment.is_corner:
                        a = segment.c
                        b = segment.end_point
                        parts.append(f"L{a.x},{a.y}L{b.x},{b.y}")
                    else:
                        a = segment.c1
                        b = segment.c2
                        c = segment.end_point
                        parts.append(f"C{a.x},{a.y} {b.x},{b.y} {c.x},{c.y}")
                parts.append("z")
            fp.write(f'<path stroke="black" fill="none" fill-rule="evenodd" d="{"".join(parts)}"/>')
            fp.write("</svg>")

        
        class CustomInterface(interfaces.Gcode):
            def __init__(self):
                super().__init__()

            # Override the laser_off method such that it also powers off the fan.
            def laser_off(self):
                return "G1 F10000 Z2"  # Turn off the fan + turn off the laser
            
            def set_laser_power(self, power):
                return "G1 F10000 Z0"


        gcode_compiler = Compiler(CustomInterface, movement_speed=10000, cutting_speed=3000, pass_depth=0)

        curves = parse_file(sys.path[0]+"\\temp\\img\\"+self.filename+".svg") # Parse an svg file into geometric curves

        gcode_compiler.append_curves(curves) 
        gcode_compiler.compile_to_file(sys.path[0]+"\\temp\\gcode\\"+self.filename+".gcode", passes=1)

        with open(sys.path[0]+"\\temp\\gcode\\"+self.filename+".gcode", 'r+') as f:
            content = f.read()
            f.seek(0, 0)
            f.write("G28\n" + '\n' + content)
        

        preview = Image.fromarray(cv2.bitwise_not(cv2.imread(sys.path[0]+"\\temp\\img\\"+self.filename+"canny.jpeg")))
        preview = ImageTk.PhotoImage(preview)
        
        self.panel.configure(image=preview)
        self.panel.image = preview
        self.panel.update_idletasks()


        print("Gen done")
        self.state=state.plot
        self.thread = threading.Thread(target=self.sendGcode, args=(), daemon=True)
        self.thread.start()
        self.btn1 = tkinter.Button(self.root, text="Pause",command=self.pause)
        self.btn1.pack(anchor=tkinter.SW, padx=10,pady=10)
        self.btn2 = tkinter.Button(self.root, text="Stop",command=self.stop)
        self.btn2.pack(anchor=tkinter.SE, padx=10,pady=10)
        #self.thread.start()
        #self.sendGcode()
        
    def pause(self):
        if self.state==state.plot:
            self.state=state.paused
        elif self.state==state.paused:
            self.state=state.plot
        
    def stop(self):
        if self.state==state.plot or self.state==state.paused:
            self.state=state.takePhoto

    def serial_ports(self):
    
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result   

    def sendGcode(self):
        #open serial
        ports = self.serial_ports()
        if "COM3" in ports:
            ports.pop(ports.index("com3"))

        if ports == []:
            print("Error opening serial")
            self.state=state.takePhoto
            self.startStream()
            return
        print("ports",ports)
        s = serial.Serial(ports[0],115200)

        f = open(sys.path[0]+"\\temp\\gcode\\"+self.filename+".gcode",'r')

        s.write(b"\r\n\r\n") # Hit enter a few times to wake the Printrbot
        time.sleep(2)   # Wait for Printrbot to initialize
        s.flushInput()  # Flush startup text in serial input

        while True:
            if self.state==state.plot:
                #send g code
                l=f.readline()
                l = l.strip() # Strip all EOL characters for streaming
                if  (l.isspace()==False and len(l)>0) :
                    print ('Sending:',  l)
                    s.write(bytearray(l + '\n','utf-8')) # Send g-code block
                    grbl_out = s.readline() # Wait for response with carriage return
                    print (grbl_out.strip())
                
            elif self.state==state.paused:
                time.sleep(0.1)
                pass
            elif self.state==state.takePhoto or self.state==state.previewPhoto or self.state==state.gen:
                break

        self.state=state.takePhoto
        self.startStream()
        return

    def on_closing(self):
        self.root.destroy()
        exit()


print("Waiting for camera")
vs = cv2.VideoCapture(0)
pba = plotter(vs)
pba.root.mainloop()