#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import numpy as np
from numpy import pi
import tkinter as tk

from calculate_with_angles import calc_azim, haversine_distance
import position

class CompassGUI:
    def __init__(self, master, serial_port, dest_lat = 50.90837, dest_lon = 11.56796):

        # Tkinter and resolution
        self.master = master
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)
        self.screen_width = self.master.winfo_screenwidth()
        self.screen_height = self.master.winfo_screenheight()
        self.compass_width = min(self.screen_width,self.screen_height)
        
        # Update rate
        self.update_delay = 50 # ms
        
        # Current navigation data
        self.dest_lat = dest_lat
        self.dest_lon = dest_lon
        
        # Trajectory tracking since app start
        self.lat_track = []
        self.lon_track = []
        self.time_track = []
        
        self.position_provider = position.PositionSerialNMEA(serial_port = serial_port)
        
        # create GUI widgets
        self.create_widgets()
        self.continuously_update_and_redraw_canvas()

    
    def create_widgets(self):
        self.master.title("Compass")
        
        init_txt = self.latlon2str(lat = self.dest_lat,lon = self.dest_lon)
        self.destination_entry = tk.Entry(self.master, width=int(0.1*self.compass_width))
        
        self.search_button = tk.Button(self.master, text="Go to", command=self.search)
        self.search_button.grid(row=0, column=1,sticky=tk.E)

        self.status_text = tk.StringVar()
        self.status_label = tk.Label(self.master, textvariable = self.status_text)
        self.status_label.grid(row=1, column=0, columnspan=2)
        
        self.compass_canvas = tk.Canvas(self.master, width=self.compass_width, height=self.compass_width, bg="black")
        self.compass_canvas.grid(row=2, column=0, columnspan=2)

        self.destination_entry.insert(0,init_txt)
        self.destination_entry.grid(row=0, column=0, sticky=tk.W)


    def on_close(self):
        self.position_provider.disconnect()        
        self.master.destroy()

    def update_and_redraw_canvas(self):
                
        if self.position_provider.update_position():
            self.status_text.set("GPS fix active.")
            self.lat_track  += self.position_provider.latitude
            self.lon_track  += self.position_provider.longitude
            self.time_track += self.position_provider.time
            
            # Calculate new angles
            """
            dlat_per_dt, dlon_per_dt, v_azim_in_rad, abs_v_in_m_per_s = calc_speed( 
                                  lat_track  = self.lat_track, 
                                  lon_track  = self.lon_track, 
                                  time_track = self.time_track
                                  )
            """
            v_azim_in_rad = self.position_provider.heading * pi / 180
            abs_v_in_m_per_s = self.position_provider.velocity
            
            dest_azim_in_rad = calc_azim(
                                  lat1_deg = self.position_provider.latitude, 
                                  lon1_deg = self.position_provider.longitude, 
                                  lat2_deg = self.dest_lat,
                                  lon2_deg = self.dest_lon,
                                  )
            dest_distance = haversine_distance(
                                  lat1_deg = self.position_provider.latitude, 
                                  lon1_deg = self.position_provider.longitude, 
                                  lat2_deg = self.dest_lat,
                                  lon2_deg = self.dest_lon,
                                  )

            # turn compass rose so that velocity points up
            n_azim_rad = - v_azim_in_rad

            # draw
            self.compass_canvas.delete("all")
            self.make_nesw(n_azim_rad)
            self.make_v_marker(v_azim_in_rad + n_azim_rad )            
            self.make_dest_marker(dest_azim_in_rad + n_azim_rad)
            self.make_left_text()
            
            speed_str = str(round(abs_v_in_m_per_s * 3.6,1)) + " km/h"
            self.compass_canvas.create_text(.5*self.compass_width, .5*self.compass_width, text= speed_str , font=("Arial", int(round(self.compass_width/13.6))), anchor=tk.N, fill="#ffff00")
            dist_str = str(round( dest_distance/1000.0 ,1)) + " km"
            self.compass_canvas.create_text(.5*self.compass_width, .6*self.compass_width, text= dist_str , font=("Arial", int(round(self.compass_width/13.6))), anchor=tk.N, fill="#ff00ff")

                
    def continuously_update_and_redraw_canvas(self):
        self.update_and_redraw_canvas()
        self.compass_canvas.after( self.update_delay, self.continuously_update_and_redraw_canvas )

    def make_nesw(self,n_azim):
        w = self.compass_width
        self.compass_canvas.create_oval(0.1*w,0.1*w,.9*w,.9*w, outline="white", width=4)
        # Ticks
        for i in np.arange(4):
            phi = n_azim+.5*i*pi
            # big 90° ticks
            self.compass_canvas.create_line( (.5 + .42 * np.sin(phi))*w, 
                                     (.5 - .42 * np.cos(phi))*w,
                                     (.5 + .35 * np.sin(phi))*w, 
                                     (.5 - .35 * np.cos(phi))*w,
                                      fill="white", width=4)
            for j in np.arange(8):
                # small 10° ticks
                alpha = (j+1) * pi / 18
                self.compass_canvas.create_line( (.5 + .4 * np.sin(phi+alpha))*w, 
                                         (.5 - .4 * np.cos(phi+alpha))*w,
                                         (.5 + .38 * np.sin(phi+alpha))*w, 
                                         (.5 - .38 * np.cos(phi+alpha))*w,
                                          fill="white", width=2)
        # NESW
        font=("Arial", int(round(w/13.6)))
        self.compass_canvas.create_text((.5 + .46 * np.sin(n_azim))*w, 
                                (.5 - .46 * np.cos(n_azim))*w,
                                 text="N", font=font, anchor=tk.CENTER, fill="white")
        self.compass_canvas.create_text((.5 + .46 * np.sin(n_azim+.5*pi))*w, 
                                (.5 - .46 * np.cos(n_azim+.5*pi))*w,
                                 text="E", font=font, anchor=tk.CENTER, fill="white")
        self.compass_canvas.create_text((.5 + .46 * np.sin(n_azim+pi))*w, 
                                (.5 - .46 * np.cos(n_azim+pi))*w,
                                 text="S", font=font, anchor=tk.CENTER, fill="white")
        self.compass_canvas.create_text((.5 + .46 * np.sin(n_azim+1.5*pi))*w, 
                                (.5 - .46 * np.cos(n_azim+1.5*pi))*w,
                                 text="W", font=font, anchor=tk.CENTER, fill="white")


    def make_v_marker(self, azim):
        w = self.compass_width
        r = .03*w # ring radius
        R = .33*w # excentricity
        l = .03*w # stripe length
        
        xcenter = 0.5*w + R * np.sin(azim)
        ycenter = 0.5*w - R * np.cos(azim)
        self.compass_canvas.create_oval(xcenter-r,
                                ycenter-r,
                                xcenter+r,
                                ycenter+r,
                                outline="yellow", width=4)
        self.compass_canvas.create_line(xcenter-r-l,
                                ycenter,
                                xcenter-r,
                                ycenter,
                                fill="yellow", width=4)
        self.compass_canvas.create_line(xcenter+r+l,
                                ycenter,
                                xcenter+r,
                                ycenter,
                                fill="yellow", width=4)
        self.compass_canvas.create_line(xcenter,
                                ycenter-r-l,
                                xcenter,
                                ycenter-r,
                                fill="yellow", width=4)
        self.compass_canvas.create_line(xcenter,
                                ycenter+r+l,
                                xcenter,
                                ycenter+r,
                                fill="yellow", width=4)
        self.compass_canvas.create_line(0.5*w,
                                0.5*w,
                                xcenter - r * np.sin(azim),
                                ycenter + r * np.cos(azim),
                                fill="yellow", width=8)

    def make_dest_marker(self,azim):
        w = self.compass_width
        d = .006*w # dot radius
        r = .06*w # ring radius
        R = .33*w # excentricity
        
        xcenter = 0.5*w + R * np.sin(azim)
        ycenter = 0.5*w - R * np.cos(azim)
        self.compass_canvas.create_oval(xcenter-d,
                                ycenter-d,
                                xcenter+d,
                                ycenter+d,
                                outline="#ff00ff", width=4)
        self.compass_canvas.create_oval(xcenter-r,
                                ycenter-r,
                                xcenter+r,
                                ycenter+r,
                                outline="#ff00ff", width=4)
        self.compass_canvas.create_line(0.5*w,
                                0.5*w,
                                xcenter - r * np.sin(azim),
                                ycenter + r * np.cos(azim),
                                fill="#ff00ff", width=12)
    
    def make_left_text(self):
        s = "GPS data:\n"
        for key in self.latest_gps_data:
            s += key + " : " + str(self.latest_gps_data[key]) + "\n"
        self.compass_canvas.create_text(5, 0, text= s , font=("Arial", 10), anchor=tk.NW, fill="red")


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

    def latlon2str(self,lat,lon):
        lat_str = "N"
        if lat < 0:
            lat_str = "S"
        lon_str = "W"
        if lon < 0:
            lon_str = "E"
        return str(abs(lat)) + lat_str + " " + str(abs(lon)) + lon_str
      

if __name__ == "__main__":
    root = tk.Tk()
    my_gui = CompassGUI(root, 
                        serial_port = "/dev/ttyUSB1",
                        )
    root.mainloop()
