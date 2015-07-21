#!/usr/bin/env python3

#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  

from gi.repository import Gtk, Gio
import cairo
import math

class MyWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Timetravel")
        #self.set_border_width(10)
        self.set_default_size(800, 600)

        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)
        hb.props.title = "Timetravel"
        self.set_titlebar(hb)

        button = Gtk.Button()
        icon = Gio.ThemedIcon(name="emblem-system-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)
        hb.pack_end(button)
        
        box = Gtk.Box(spacing=6)

        button = Gtk.Button(label="Snapshot")
        box.add(button)

        button = Gtk.Button()
        icon = Gio.ThemedIcon(name="zoom-in-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)
        box.add(button)
        
        hb.pack_start(box)
        
        
        self.darea = Gtk.DrawingArea()
        self.darea.connect("draw", self.on_draw)
        #self.darea.set_events(Gdk.EventMask.BUTTON_PRESS_MASK)        
        self.add(self.darea)

    def on_draw(self, wid, cr):

        cr.translate(700,250)
        #cr.scale(800,600)
        
        cr.set_source_rgb(0.6, 0.6, 0.6)
        cr.set_line_width(1)
        cr.set_dash([10.0, 6.0])
        cr.move_to(0, -250)
        cr.line_to(0, 210)
        cr.stroke()
        cr.set_dash([])
        nowTxt = "now"
        cr.set_source_rgb(0,0,0)
        cr.set_font_size(15)
        xbearing, ybearing, width, height, xadvance, yadvance = cr.text_extents(nowTxt)
        cr.move_to(-width/2, 210+height+10)
        cr.show_text(nowTxt)
        cr.stroke()
        

        cr.set_source_rgb(0.2, 0.2, 0.7)
        cr.set_line_width(3)

        cr.move_to(-200, 0)
        cr.line_to(0, 0) 
        cr.stroke()
        
        drawSnapshot(cr, "current", 0, 0, 0.2, 0.7, 0.2)
        drawSnapshot(cr, "snap-2015-07-16", -200, 0, 0.2, 0.2, 0.7)
        
def drawSnapshot (cr, name, x, y, r, g, b):
    cr.set_source_rgb(r,g,b)
    cr.arc(x, y, 8, 0, 2*math.pi)
    cr.fill()
    cr.set_source_rgb(0,0,0)
    cr.set_font_size(15)
    xbearing, ybearing, width, height, xadvance, yadvance = cr.text_extents(name)
    cr.move_to(x-width/2, y+height+10)
    cr.show_text(name)
    cr.stroke()

def drawNowAxis (cr):
    pass

win = MyWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
