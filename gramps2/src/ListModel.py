#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000  Donald N. Allingham
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

from gobject import TYPE_STRING, TYPE_PYOBJECT
import gtk

class ListModel:
    def __init__(self,tree,dlist,select_func=None,event_func=None,mode=gtk.SELECTION_SINGLE):
        self.tree = tree
        l = len(dlist)
        self.mylist = [TYPE_STRING]*l + [TYPE_PYOBJECT]

        self.tree.set_rules_hint(gtk.TRUE)
        self.tree.set_enable_search(gtk.TRUE)
        self.tree.set_search_column(gtk.TRUE)
        self.new_model()
        self.selection = self.tree.get_selection()
        self.selection.set_mode(mode)
        self.mode = mode
        self.data_index = l

        self.cids = []
        
        cnum = 0
        for name in dlist:
            renderer = gtk.CellRendererText()
            column = gtk.TreeViewColumn(name[0],renderer,text=cnum)
            column.set_min_width(name[2])
            if name[0] == '':
                column.set_visible(gtk.FALSE)
            else:
                column.set_resizable(gtk.TRUE)
            if name[1] == -1:
                column.set_clickable(gtk.FALSE)
            else:
                column.set_clickable(gtk.TRUE)
                column.set_sort_column_id(name[1])

            cnum = cnum + 1
            self.cids.append(name[1])
            if name[1] != -1:
                self.tree.append_column(column)

        if self.cids[0] > 0:
            self.model.set_sort_column_id(self.cids[0],gtk.SORT_ASCENDING)
        self.connect_model()
        
        if select_func:
            self.selection.connect('changed',select_func)
        if event_func:
            self.double_click = event_func
            self.tree.connect('event',self.button_press)

    def new_model(self):
        self.model = gtk.ListStore(*self.mylist)

    def connect_model(self):
        self.tree.set_model(self.model)
        self.sort()

    def sort(self):
        val = self.model.get_sort_column_id()
        col = val[0]
        if col > 0:
            self.model.set_sort_column_id(col,val[1])
        else:
            self.model.set_sort_column_id(self.cids[0],val[1])
        self.model.sort_column_changed()
        
    def get_selected(self):
        return self.selection.get_selected()

    def get_selected_objects(self):
        if self.mode == gtk.SELECTION_SINGLE:
            store,iter = self.selection.get_selected()
            if iter:
                return [self.model.get_value(iter,self.data_index)]
            else:
                return []
        else:
            mlist = []
            self.selection.selected_foreach(self.blist,mlist)
            return mlist

    def blist(self,store,path,iter,list):
        list.append(self.model.get_value(iter,self.data_index))

    def clear(self):
        self.model.clear()

    def remove(self,iter):
        self.model.remove(iter)
        
    def get_row(self,iter):
        row = self.model.get_path(iter)
        return row[0]

    def select_row(self,row):
        self.selection.select_path((row))
    
    def get_object(self,iter):
        return self.model.get_value(iter,self.data_index)
        
    def add(self,data,info=None,select=0):
        iter = self.model.append()
        col = 0
        for object in data:
            self.model.set_value(iter,col,object)
            col = col + 1
        self.model.set_value(iter,col,info)
        if select:
            self.selection.select_iter(iter)
        return iter

    def add_and_select(self,data,info=None):
        iter = self.model.append()
        col = 0
        for object in data:
            self.model.set_value(iter,col,object)
            col = col + 1
        self.model.set_value(iter,col,info)
        self.selection.select_iter(iter)
        
    def button_press(self,obj,event):
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
            self.double_click(obj)
            return 1
