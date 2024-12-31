# -*- coding: utf-8 -*-
import os
import sys
import time
import tempfile
import tkinter as Tk_
from tkinter import ttk
from tkinter.ttk import Spinbox
from tkinter.font import Font, families as font_families
from tkinter.simpledialog import Dialog, SimpleDialog
from plink.ipython_tools import IPythonTkRoot
from . import filedialog

    
def nominal_font_dict(tk_font):
    """
    Like Font.actual() but not messed up by GNOME scaling factors on
    Linux.
    """
    return {key:tk_font.cget(key) for key in tk_font.actual()}


class SnapPyStyle:
    def __init__(self):
        self.ttk_style = ttk_style = ttk.Style()
        # The windowBG, groupBG and subgroupBG colors can be used to match Tk objects to
        # Ttk containers.
        if sys.platform == 'darwin':
            try:
                # check if our Tk supports the new semantic colors
                test = Tk_._default_root.winfo_rgb('systemWindowBackgroundColor1')
                self.windowBG = 'systemWindowBackgroundColor'
                self.groupBG = 'systemWindowBackgroundColor1'
                self.subgroupBG = 'systemWindowBackgroundColor2'
            except:
                # These will be wrong in dark mode.
                self.windowBG = '#ededed'
                self.groupBG = '#e5e5e5'
                self.subgroupBG = '#dddddd'
        else:
            self.windowBG = ttk_style.lookup('TLabelframe', 'background')
            self.groupBG = self.subgroupBG = self.windowBG

        self.font = ttk_style.lookup('TLabel', 'font')
        if self.font == '':
            self.font = 'TkDefaultFont'
        # TLabel.font and TLabelframe.Label.font differ in Tk 9.0 (at
        # least on macOS).  We restore the Tk 8.6 behavior.
        self.ttk_style.configure('TLabelframe.Label',
                                 font=self.font)
        self.font_info = fi = nominal_font_dict(Font(font=self.font))
        fi['size'] = int(str(fi['size']))
        # Linux makes the treeview rows too small, at least with hi-dpi displays.
        if sys.platform == 'linux':
            self.ttk_style.configure('Treeview', rowheight=2 * fi['size'])

class ViewerWindow(Tk_.Toplevel):
    def __init__(self, view_class, *args, **kwargs):
        window_type = kwargs.pop('window_type', 'untyped')
        self.root = kwargs.pop('root', self._get_root(window_type))
        Tk_.Toplevel.__init__(self, self.root, class_='snappy')
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.title(string=kwargs.pop('title', ''))
        self.view = view_class(self, *args, **kwargs)
        self.view.pack(expand=True, fill=Tk_.BOTH)
        self.update_idletasks()

    def __repr__(self):
        return 'New window: %s\n' % self.title()

    def _get_root(self, window_type):
        if Tk_._default_root:
            return Tk_._default_root
        root = IPythonTkRoot(window_type=window_type)
        root.withdraw()
        return root

    def save_image(self):
        """
        Helper for the save_image menu command of a ViewerWindow.
        It expects to be passed the view Frame (not the parent Toplevel)
        and it saves a PNG image of the current state of the view.
        """
        view = self.view
        savefile = filedialog.asksaveasfile(
            parent=self,
            mode='wb',
            title='Save Image As PNG Image File',
            defaultextension='.png',
            filetypes=[
                ("PNG image files", "*.png *.PNG", ""),
                ("All files", "")])
        if savefile:
            view.widget.save_image_window_resolution(savefile)

    def close(self, event=None):
        if hasattr(self.view, 'delete_resource'):
            self.view.delete_resource()
        self.view = None
        self.destroy()

    def add_help(self):
        pass

    def edit_actions(self):
        return {}

    def test(self):
        print('Testing viewer for %s' % self.title())
        time.sleep(0.5)
        if hasattr(self.view, 'test'):
            if not self.view.winfo_ismapped():
                self.view.wait_visibility()
            self.update()
            time.sleep(0.5)
            self.view.focus_force()
            self.view.test()
            time.sleep(0.5)
            self.close()
