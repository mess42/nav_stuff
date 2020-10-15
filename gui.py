#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import serial

import numpy as np
from numpy import pi
import tkinter as tk

from calculate_with_angles import calc_azim
import decode_nmea

class CompassGUI:
    def __init__(self, master, serial_port, dest_lat = 50.90837, dest_lon = 11.56796):

        self.serial_connection = serial.Serial( port=serial_port, timeout = 0.2 )
        self.serial_connection.isOpen()
        print("Serial Connection Established.")
        
        self.master = master
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.canvas_width = 300 # px
        self.update_delay = 250 # ms
        
        self.dest_lat = dest_lat
        self.dest_lon = dest_lon
        self.latest_gps_data = {"time":      "",
                                "is_active": False,
                                "latitude":  50,
                                "longitude": 12,
                                "speed":     0,
                                "azimuth":   0,
                                "date":      ""
                                }
        
        self.create_widgets()
        self.continuously_update_and_redraw_canvas()

    
    def create_widgets(self):
        self.master.title("Compass")
                
        self.destination_entry = tk.Entry(self.master)
        self.destination_entry.grid(row=0, column=0)

        self.search_button = tk.Button(self.master, text="Go!", command=self.search)
        self.search_button.grid(row=0,column=1)
        
        self.canvas = tk.Canvas(self.master, width=self.canvas_width, height=self.canvas_width, bg="black")
                
        self.canvas.grid(row=1, column=0, columnspan=2)

    def on_close(self):
        self.serial_connection.close()
        print("Serial Connection closed.")
        self.master.destroy()

    def update_and_redraw_canvas(self):
        
        sentence = self.serial_connection.readline().decode("utf-8")
        
        if sentence.startswith("$GPRMC"):
            self.latest_gps_data =  decode_nmea.decode_gprmc_sentence(sentence)
            print( self.latest_gps_data )
        
            # Calculate new angles
            n_azim_rad = 0
            v_azim_rad = self.latest_gps_data["azimuth"] * pi /180.
            self.dest_azim_rad = calc_azim(lat1_deg = self.latest_gps_data["latitude"], 
                                      lon1_deg = self.latest_gps_data["longitude"], 
                                      lat2_deg = self.dest_lat,
                                      lon2_deg = self.dest_lon,
                                      )
            
            # draw
            self.canvas.delete("all")
            self.make_nesw(n_azim_rad)
            self.make_v_marker(v_azim_rad + n_azim_rad )
            self.make_dest_marker(self.dest_azim_rad + n_azim_rad)
            self.make_left_text()
        
    def continuously_update_and_redraw_canvas(self):
        self.update_and_redraw_canvas()
        self.canvas.after( self.update_delay, self.continuously_update_and_redraw_canvas )

    def make_nesw(self,n_azim):
        w = self.canvas_width
        self.canvas.create_oval(0.1*w,0.1*w,.9*w,.9*w, outline="white", width=4)
        # Ticks
        for i in np.arange(4):
            phi = n_azim+.5*i*pi
            # big 90° ticks
            self.canvas.create_line( (.5 + .42 * np.sin(phi))*w, 
                                     (.5 - .42 * np.cos(phi))*w,
                                     (.5 + .35 * np.sin(phi))*w, 
                                     (.5 - .35 * np.cos(phi))*w,
                                      fill="white", width=4)
            for j in np.arange(8):
                # small 10° ticks
                alpha = (j+1) * pi / 18
                self.canvas.create_line( (.5 + .4 * np.sin(phi+alpha))*w, 
                                         (.5 - .4 * np.cos(phi+alpha))*w,
                                         (.5 + .38 * np.sin(phi+alpha))*w, 
                                         (.5 - .38 * np.cos(phi+alpha))*w,
                                          fill="white", width=2)
        # NESW
        font=("Arial", int(round(w/13.6)))
        self.canvas.create_text((.5 + .46 * np.sin(n_azim))*w, 
                                (.5 - .46 * np.cos(n_azim))*w,
                                 text="N", font=font, anchor=tk.CENTER, fill="white")
        self.canvas.create_text((.5 + .46 * np.sin(n_azim+.5*pi))*w, 
                                (.5 - .46 * np.cos(n_azim+.5*pi))*w,
                                 text="E", font=font, anchor=tk.CENTER, fill="white")
        self.canvas.create_text((.5 + .46 * np.sin(n_azim+pi))*w, 
                                (.5 - .46 * np.cos(n_azim+pi))*w,
                                 text="S", font=font, anchor=tk.CENTER, fill="white")
        self.canvas.create_text((.5 + .46 * np.sin(n_azim+1.5*pi))*w, 
                                (.5 - .46 * np.cos(n_azim+1.5*pi))*w,
                                 text="W", font=font, anchor=tk.CENTER, fill="white")


    def make_v_marker(self, azim):
        w = self.canvas_width
        r = .03*w # ring radius
        R = .33*w # excentricity
        l = .03*w # stripe length
        
        xcenter = 0.5*w + R * np.sin(azim)
        ycenter = 0.5*w - R * np.cos(azim)
        self.canvas.create_oval(xcenter-r,
                                ycenter-r,
                                xcenter+r,
                                ycenter+r,
                                outline="yellow", width=4)
        self.canvas.create_line(xcenter-r-l,
                                ycenter,
                                xcenter-r,
                                ycenter,
                                fill="yellow", width=4)
        self.canvas.create_line(xcenter+r+l,
                                ycenter,
                                xcenter+r,
                                ycenter,
                                fill="yellow", width=4)
        self.canvas.create_line(xcenter,
                                ycenter-r-l,
                                xcenter,
                                ycenter-r,
                                fill="yellow", width=4)
        self.canvas.create_line(xcenter,
                                ycenter+r+l,
                                xcenter,
                                ycenter+r,
                                fill="yellow", width=4)
        self.canvas.create_line(0.5*w,
                                0.5*w,
                                xcenter - r * np.sin(azim),
                                ycenter + r * np.cos(azim),
                                fill="yellow", width=8)

    def make_dest_marker(self,azim):
        w = self.canvas_width
        d = .006*w # dot radius
        r = .06*w # ring radius
        R = .33*w # excentricity
        
        xcenter = 0.5*w + R * np.sin(azim)
        ycenter = 0.5*w - R * np.cos(azim)
        self.canvas.create_oval(xcenter-d,
                                ycenter-d,
                                xcenter+d,
                                ycenter+d,
                                outline="#ff00ff", width=4)
        self.canvas.create_oval(xcenter-r,
                                ycenter-r,
                                xcenter+r,
                                ycenter+r,
                                outline="#ff00ff", width=4)
        self.canvas.create_line(0.5*w,
                                0.5*w,
                                xcenter - r * np.sin(azim),
                                ycenter + r * np.cos(azim),
                                fill="#ff00ff", width=12)
    
    def make_left_text(self):
        s = "GPS data:\n"
        for key in self.latest_gps_data:
            s += key + " : " + str(self.latest_gps_data[key]) + "\n"
        s += "\n\nDestination data:\n"
        s += "latitude : " + str(self.dest_lat) + "\n"
        s += "longitude : " + str(self.dest_lon) + "\n"
        s += "azimuth : " + str(self.dest_azim_rad *180/pi)
        self.canvas.create_text(5, 0, text= s , font=("Arial", 10), anchor=tk.NW, fill="red")


    def search(self):
        txt = self.destination_entry.get()
        
        # Try to interpret the entry as latitude longitude
        latlon_split_txt = txt.split()
        latlon = {}
        if len(latlon_split_txt) == 2:
            try:
                flo0  = latlon_split_txt[0][:-1]
                last0 = latlon_split_txt[0][-1].upper()
                flo1  = latlon_split_txt[1][:-1]
                last1 = latlon_split_txt[1][-1].upper()
                
                if last0 in ["N","S"]:
                    lat = float( flo0 ) * ( 1 - 2 * (last0 == "S") )
                    if not np.isnan(lat):
                        latlon["lat"] = lat
                if last1 in ["W","E"]:
                    lon = float( flo1 ) * ( 1 - 2 * (last1 == "W") )
                    if not np.isnan(lon):
                        latlon["lon"] = lon
            except:
                pass
        if "lat" in latlon and "lon" in latlon:
            self.dest_lon = latlon["lon"]
            self.dest_lat = latlon["lat"]
        else:
            print("failed to read input")


       
    #def update(self):
        # make fullscreen
        #screen_width = self.master.winfo_screenwidth()
        #screen_height = self.master.winfo_screenheight()
        #fullscreen_str = str(int(screen_width)) + "x" + str(int(screen_height))
        #self.master.geometry(fullscreen_str)
        
        #self.label.configure(text="%i s" % self.seconds)
        #self.seconds += 1
        #self.label.after(1000, self.update)


if __name__ == "__main__":
    root = tk.Tk()
    my_gui = CompassGUI(root, 
                        serial_port = "/dev/ttyUSB1",
                        )
    root.mainloop()