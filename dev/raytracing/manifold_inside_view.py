import tkinter as Tk_
import tkinter.ttk as ttk

from snappy import Manifold

from snappy.gui import WindowOrFrame

import math

import sys
import time

from snappy.CyOpenGL import get_gl_string

from .manifold_inside_view_widget import *

def attach_scale_and_label_to_uniform(uniform_dict,
                                      key, update_function, scale, label,
                                      format_string = None,
                                      index = None):
    uniform_type, value = uniform_dict[key]

    if index is None:
        if not uniform_type in ['int', 'float']:
            raise Exception("Unsupported uniform slider type")
    else:
        if uniform_type == 'int[]':
            uniform_type = 'int'
        elif uniform_type == 'float[]':
            uniform_type = 'float'
        elif uniform_type == 'vec2':
            uniform_type = 'float'
        else:
            raise Exception("Unsupported uniform slider type")

        value = value[index]

    if format_string is None:
        if uniform_type == 'int':
            format_string = '%d'
        else:
            format_string = '%.2f'

    scale.configure(value = value)
    label.configure(text = format_string % value)
    
    def scale_command(t,
                      uniform_dict = uniform_dict,
                      key = key,
                      format_string = format_string,
                      uniform_type = uniform_type,
                      update_function = update_function,
                      label = label,
                      index = index):

        value = float(t)
        if uniform_type == 'int':
            value = int(value)
        if index is None:
            uniform_dict[key] = (uniform_type, value)
        else:
            uniform_dict[key][1][index] = value
        label.configure(text = format_string % value)
        if update_function:
            update_function()

    scale.configure(command = scale_command)

    def update_scale(uniform_dict = uniform_dict,
                     key = key,
                     format_string = format_string,
                     uniform_type = uniform_type,
                     scale = scale,
                     label = label,
                     index = index):

        uniform_type, value = uniform_dict[key]
        if not index is None:
            value = value[index]
        if uniform_type == 'int':
            value = int(value)
        else:
            value = float(value)
        label.configure(text = format_string % value)
        scale.configure(value = value)

    return update_scale

def create_horizontal_scale_for_uniforms(
    window, uniform_dict, key, title, row, from_, to, update_function,
    index = None,
    format_string = None,
    column = 0):

    if title:
        title_label = ttk.Label(window, text = title)
        title_label.grid(row = row, column = column, sticky = Tk_.NSEW)
        column += 1

    scale = ttk.Scale(window, from_ = from_, to = to,
                      orient = Tk_.HORIZONTAL)
    scale.grid(row = row, column = column, sticky = Tk_.NSEW)
    column += 1

    value_label = ttk.Label(window)
    value_label.grid(row = row, column = column, sticky = Tk_.NSEW)
    
    return attach_scale_and_label_to_uniform(
        uniform_dict, key, update_function, scale, value_label,
        index = index,
        format_string = format_string)
    
class FpsLabelUpdater:
    def __init__(self, label):
        self.label = label
        self.num_iterations = 0
        self.total_time = 0.0
        self.last_time = time.time()

    def __call__(self, t):
        self.num_iterations += 1
        self.total_time += t
        if self.num_iterations > 50 or time.time() - self.last_time > 2.0:
            current_time = time.time()
            fps = self.num_iterations / (current_time - self.last_time)
            time_ms = 1000 * self.total_time / self.num_iterations

            self.label.configure(text = '%.1ffps (%dms)' % (fps, time_ms))
            self.last_time = current_time
            self.num_iterations = 0
            self.total_time = 0.0
    

class InsideManifoldSettings:
    def __init__(self, main_widget):
        self.toplevel_widget = Tk_.Tk()
        self.toplevel_widget.title("Settings")
        
        self.toplevel_widget.columnconfigure(0, weight = 0)
        self.toplevel_widget.columnconfigure(1, weight = 1)
        self.toplevel_widget.columnconfigure(2, weight = 0)

        row = 0
        create_horizontal_scale_for_uniforms(
            self.toplevel_widget,
            main_widget.ui_uniform_dict,
            key = 'maxSteps',
            title = 'Max Steps',
            row = row,
            from_ = 1,
            to = 100,
            update_function = main_widget.redraw_if_initialized)

        debug_with_fudge = False
        if debug_with_fudge:
            row += 1
            create_horizontal_scale_for_uniforms(
                self.toplevel_widget,
                main_widget.ui_uniform_dict,
                key = 'fudge',
                title = 'Fudge',
                row = row,
                from_ = -2.0,
                to = 2.0,
                update_function = main_widget.redraw_if_initialized)
            
        row += 1
        create_horizontal_scale_for_uniforms(
            self.toplevel_widget,
            main_widget.ui_uniform_dict,
            key = 'maxDist',
            title = 'Max Distance',
            row = row,
            from_ = 1.0,
            to = 28.0,
            update_function = main_widget.redraw_if_initialized)

        row += 1
        create_horizontal_scale_for_uniforms(
            self.toplevel_widget,
            main_widget.ui_uniform_dict,
            key = 'subpixelCount',
            title = 'Subpixel count',
            row = row,
            from_ = 1,
            to = 4,
            update_function = main_widget.redraw_if_initialized)

        row += 1
        create_horizontal_scale_for_uniforms(
            self.toplevel_widget,
            main_widget.ui_uniform_dict,
            key = 'edgeThickness',
            title = 'Face boundary thickness',
            row = row,
            from_ = 0.0,
            to = 0.1,
            update_function = main_widget.redraw_if_initialized,
            format_string = '%.3f')

        row += 1
        create_horizontal_scale_for_uniforms(
            self.toplevel_widget,
            main_widget.ui_parameter_dict,
            key = 'insphere_scale',
            title = 'Insphere scale',
            row = row,
            from_ = 0.0,
            to = 3.0,
            update_function = main_widget.recompute_raytracing_data_and_redraw,
            format_string = '%.2f')

        row += 1
        create_horizontal_scale_for_uniforms(
            self.toplevel_widget,
            main_widget.ui_parameter_dict,
            key = 'edgeTubeRadius',
            title = 'Edge thickness',
            row = row,
            from_ = 0.0,
            to = 0.75,
            update_function = main_widget.redraw_if_initialized)

        row += 1
        create_horizontal_scale_for_uniforms(
            self.toplevel_widget,
            main_widget.ui_parameter_dict,
            key = 'translationVelocity',
            title = 'Translation Speed',
            row = row,
            from_ = 0.1,
            to = 1.0,
            update_function = None)

        row += 1
        create_horizontal_scale_for_uniforms(
            self.toplevel_widget,
            main_widget.ui_parameter_dict,
            key = 'rotationVelocity',
            title = 'Rotation Speed',
            row = row,
            from_ = 0.1,
            to = 1.0,
            update_function = None)

        row += 1
        create_horizontal_scale_for_uniforms(
            self.toplevel_widget,
            main_widget.ui_uniform_dict,
            key = 'lightBias',
            title = 'Light bias',
            row = row,
            from_ = 0.3,
            to = 4.0,
            update_function = main_widget.redraw_if_initialized)

        row += 1
        create_horizontal_scale_for_uniforms(
            self.toplevel_widget,
            main_widget.ui_uniform_dict,
            key = 'lightFalloff',
            title = 'Light falloff',
            row = row,
            from_ = 0.1,
            to = 2.0,
            update_function = main_widget.redraw_if_initialized)

        row += 1
        create_horizontal_scale_for_uniforms(
            self.toplevel_widget,
            main_widget.ui_uniform_dict,
            key = 'brightness',
            title = 'Brightness',
            row = row,
            from_ = 0.3,
            to = 3.0,
            update_function = main_widget.redraw_if_initialized)

class InsideManifoldGUI(WindowOrFrame):
    def __init__(self, manifold, parent = None, title = '', window_type = 'untyped'):

        WindowOrFrame.__init__(self,
                               parent = parent,
                               title = title,
                               window_type = window_type)

        main_frame = self.create_frame_with_main_widget(
            self.container, manifold)

        self.filling_list = [
            ('vec2', list(d['filling']))
            for d in self.main_widget.manifold.cusp_info() ]

        self.manifold_copy = manifold.copy()
        
        row = 0
        self.notebook = ttk.Notebook(self.container)
        self.notebook.grid(row = row, column = 0, sticky = Tk_.NSEW,
                           padx = 0, pady = 0, ipady = 0)

        self.notebook.add(self.create_cusp_areas_frame(self.container),
                          text = 'Cusp areas')
        
        self.notebook.add(self.create_fillings_frame(self.container),
                          text = 'Fillings')

        self.notebook.add(self.create_other_frame(self.container),
                          text = 'Other')

        row += 1
        main_frame.grid(row = row, column = 0, sticky = Tk_.NSEW)
        self.container.columnconfigure(0, weight = 1)
        self.container.rowconfigure(row, weight = 1)

        row += 1
        status_frame = self.create_status_frame(
            self.container)
        status_frame.grid(row = row, column = 0, sticky = Tk_.NSEW)

        attach_scale_and_label_to_uniform(
            uniform_dict = self.main_widget.ui_uniform_dict,
            key = 'fov',
            update_function = self.main_widget.redraw_if_initialized,
            scale = self.fov_scale,
            label = self.fov_label,
            format_string = '%.1f')

        self.main_widget.report_time_callback = FpsLabelUpdater(
            self.fps_label)

    def create_cusp_areas_frame(self, parent):
        frame = ttk.Frame(parent)

        frame.columnconfigure(0, weight = 0)
        frame.columnconfigure(1, weight = 1)
        frame.columnconfigure(2, weight = 0)

        row = 0

        for i in range(self.main_widget.manifold.num_cusps()):
            create_horizontal_scale_for_uniforms(
                frame,
                uniform_dict = self.main_widget.ui_parameter_dict,
                key = 'cuspAreas',
                title = 'Cusp %d' % i,
                from_ = 0.0,
                to = 5.0,
                row = row,
                update_function = self.main_widget.recompute_raytracing_data_and_redraw,
                index = i)
            row += 1
            
        return frame

    def create_fillings_frame(self, parent):
        frame = ttk.Frame(parent)

        frame.columnconfigure(0, weight = 0)
        frame.columnconfigure(1, weight = 1)
        frame.columnconfigure(2, weight = 0)
        frame.columnconfigure(3, weight = 1)
        frame.columnconfigure(4, weight = 0)

        row = 0

        subframe = ttk.Frame(frame)
        subframe.grid(row = row, column = 0, columnspan = 5)
        subframe.columnconfigure(0, weight = 1)
        subframe.columnconfigure(1, weight = 0)
        subframe.columnconfigure(2, weight = 0)
        subframe.columnconfigure(3, weight = 1)
        
        settings_button = Tk_.Button(
            subframe, text = "Recompute hyp. structure",
            command = lambda : self.update_fillings(init = True))
        settings_button.grid(row = 0, column = 1)

        snap_button = Tk_.Button(
            subframe, text = "Round to integers",
            command = self.round_fillings)
        snap_button.grid(row = 0, column = 2)

        row += 1

        self.filling_scale_updates = []
        
        for i in range(self.main_widget.manifold.num_cusps()):
            self.filling_scale_updates.append(
                create_horizontal_scale_for_uniforms(
                    frame,
                    self.filling_list,
                    key = i,
                    column = 0,
                    index = 0,
                    title = 'Cusp %d' % i,
                    row = row,
                    from_ = -15,
                    to = 15,
                    update_function = self.update_fillings))

            self.filling_scale_updates.append(
                create_horizontal_scale_for_uniforms(
                    frame,
                    self.filling_list,
                    key = i,
                    column = 3,
                    index = 1,
                    title = None,
                    row = row,
                    from_ = -15,
                    to = 15,
                    update_function = self.update_fillings))

            row += 1

        return frame

    def create_other_frame(self, parent):
        frame = ttk.Frame(parent)
        
        settings_button = Tk_.Button(frame, text = "Settings",
                                     command = self.launch_settings)
        settings_button.grid(row = 0, column = 0)

        return frame

    def create_frame_with_main_widget(self, parent, manifold):
        frame = ttk.Frame(parent)

        column = 0

        self.main_widget = ManifoldInsideViewWidget(
            manifold, frame,
            width = 600, height = 500, double = 1, depth = 1)
        self.main_widget.grid(row = 0, column = column, sticky = Tk_.NSEW)
        self.main_widget.make_current()
        print(get_gl_string('GL_VERSION'))
        frame.columnconfigure(column, weight = 1)
        frame.rowconfigure(0, weight = 1)

        column += 1
        self.fov_scale = ttk.Scale(frame, from_ = 20, to = 160,
                                   orient = Tk_.VERTICAL)
        self.fov_scale.grid(row = 0, column = column, sticky = Tk_.NSEW)

        return frame

    def create_status_frame(self, parent):
        frame = ttk.Frame(parent)

        column = 0
        label = ttk.Label(frame, text = "FOV:")
        label.grid(row = 0, column = column)

        column += 1
        self.fov_label = ttk.Label(frame)
        self.fov_label.grid(row = 0, column = column)

        column += 1
        self.fps_label = ttk.Label(frame)
        self.fps_label.grid(row = 0, column = column)

        return frame

    def launch_settings(self):
        settings = InsideManifoldSettings(self.main_widget)
        settings.toplevel_widget.focus_set()

    def update_fillings(self, init = False):

        if init:
            self.main_widget.manifold = self.manifold_copy.copy()
            self.main_widget.reset_view_state()

        self.main_widget.manifold.dehn_fill(
            [ value for uniform_type, value in  self.filling_list])

        self.main_widget.recompute_raytracing_data_and_redraw()
        
    def round_fillings(self):
        for f in self.filling_list:
            for i in [0, 1]:
                f[1][i] = float(round(f[1][i]))
        for u in self.filling_scale_updates:
            u()
        self.update_fillings()

class PerfTest:
    def __init__(self, widget, num_iterations = 20):
        self.widget = widget
        self.m = unit_3_vector_and_distance_to_O13_hyperbolic_translation(
            [ 0.3 * math.sqrt(2.0), 0.4 * math.sqrt(2.0), 0.5 * math.sqrt(2.0) ],
            0.1 / num_iterations)
        self.num_iterations = num_iterations
        self.current_iteration = 0
        self.total_time = 0.0
        
        self.widget.report_time_callback = self.report_time

        self.widget.after(250, self.redraw)

        self.widget.focus_set()
        self.widget.mainloop()


    def report_time(self, t):
        self.total_time += t
        
    def redraw(self):
        self.current_iteration += 1
        if self.current_iteration == self.num_iterations:
            print("Total time: %.1fms" % (1000 * self.total_time))
            print("Time: %.1fms" % (1000 * self.total_time / self.num_iterations))
            sys.exit(0)

        self.widget.view_state = self.widget.raytracing_data.update_view_state(
            self.widget.view_state, self.m)
        
        self.widget.redraw_if_initialized()
        self.widget.after(250, self.redraw)
        
def run_perf_test(): 
    gui = InsideManifoldGUI(Manifold("m004"))

    PerfTest(gui.main_widget)
