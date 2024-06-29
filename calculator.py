import math
from string import digits, ascii_letters
import pygame
from settings import *
import customtkinter as ctk
from misc_components import APIObject
from PIL import Image
from tkinter import dialog
from pathlib import Path


class GraphCalculator(APIObject):
    def __init__(self, api_file: FileType, send_graph_info_func: Callable[[str, int], None], remove_graph_info_func: Callable[[int], None]) -> None:
        super().__init__(api_file)
        
        ctk.set_default_color_theme('blue')
        ctk.set_appearance_mode('dark')
        ctk.set_window_scaling(0.75)
        ctk.set_widget_scaling(0.75)
        
        self.root = ctk.CTk()
        
        self.scr_width = 1200
        self.scr_height = 650
        
        self.root.geometry(f'{self.scr_width}x{self.scr_height}')
        self.root.minsize(self.scr_width, self.scr_height)
        
        self.api_info[GRAPH_CALC_INFO_ID][GRAPH_CALC_RUNNING_ID] = True
        self.write_to_api(self.api_info)
        
        self.send_graph_info_func = send_graph_info_func
        self.remove_graph_info_func = remove_graph_info_func
        
        self.frame_id = 'frame'
        self.menu_bar_frame_id = 'menuframebar'
        self.index_id = 'index'
        self.cursor_id = 'cursor'
        self.keystrokes_id = 'keystrokes'
        self.color_sliders_id = 'colorsliders'
        self.color_entry_id = 'colorentry'
        self.color_button_id = 'colorbutton'
        self.color_entry_repr_id = 'colorentryrepr'
        self.color_editor_enables_id = 'coloreditorenables'
        self.toogle_state_button_id = 'tooglestatebutton'
        
        self.funtion_calcs_info = {}
        
        self.funcs_amt = 0
        
        self.display_color = '#111111'
        self.frame_bar_color = 'black'
        self.cursor_char = '|'
        
        self.math_func_strings = []
        for name, probaable_func in [(n, p_f) for n, p_f in math.__dict__.items() if isinstance(p_f, Callable)]:
            try:
                if not isinstance(probaable_func(10), int | float):
                    raise TypeError('Whatever')
                if isinstance(probaable_func(10), bool):
                    raise TypeError('Whatever')
            except TypeError:
                continue
            except ValueError:
                pass
            self.math_func_strings.append(name)
        self.math_func_strings.sort()
        
        self.ascii_letters_without_x = ascii_letters.replace(X.lower(), '').replace(X.upper(), '')
        
        self.math_func_strings_ir = dict([(self._get_funcs_replacement_fmt(self.ascii_letters_without_x[i]), name) for i, name in enumerate(self.math_func_strings)])
        
        self.menubar_bg_frame = ctk.CTkFrame(self.root, height=20, fg_color=self.frame_bar_color, corner_radius=0)
        self.menubar_bg_frame.pack(fill='x')
        self.bg_display_frame = ctk.CTkFrame(self.root)
        self.bg_display_frame.pack(fill='both', expand=True)
        
        self.frame_menu_bar = ctk.CTkFrame(self.menubar_bg_frame, corner_radius=0, fg_color=self.frame_bar_color, height=20)
        self.frame_menu_bar.pack(side='left', pady=2, fill='x', expand=True)
        ctk.CTkButton(self.menubar_bg_frame, 20, 20, text='+', corner_radius=10, command=self.add_sub_calc).pack(side='right')
        
        self.add_sub_calc(False)
    
    def _get_funcs_replacement_fmt(self, func_text):
        return f'a{func_text + self.ascii_letters_without_x[(ord(func_text) + 3)%len(self.ascii_letters_without_x)]*20 }askdasjdn'
    
    def _make_sub_calc(self, name: str):
        frame = self.funtion_calcs_info[name][self.frame_id]
        index = self.funtion_calcs_info[name][self.index_id]
        
        master_frame1 = ctk.CTkFrame(frame)
        master_frame1.pack(side='top', pady=2, fill='x', expand=True)
        master_frame2 = ctk.CTkFrame(frame)
        master_frame2.pack(side='left', pady=2, fill='both', expand=True)
        master_frame3 = ctk.CTkFrame(frame)
        master_frame3.pack(side='top', pady=2, fill='y', expand=True)
        master_frame4 = ctk.CTkFrame(frame, fg_color='transparent')
        master_frame4.pack(side='bottom', pady=2, fill='both', expand=True)
        
        sub_frame1 = ctk.CTkScrollableFrame(master_frame1, fg_color=self.display_color, height=ctk.CTkFont()._size * 2, orientation='horizontal', scrollbar_button_color=self.display_color, scrollbar_button_hover_color='#f0f0f0')
        sub_frame1.pack(side='left', fill='x', expand=True)
        cancel_buttons_frame = ctk.CTkFrame(master_frame1)
        cancel_buttons_frame.pack(side='right', padx=10, pady=5)
        ctk.CTkButton(cancel_buttons_frame, text='<', width=30, command=lambda: self.backspace_text(name, display_label)).pack()
        ctk.CTkButton(cancel_buttons_frame, text='C', width=30, command=lambda: self.clear_all(name, display_label)).pack()
        
        slider_frame = ctk.CTkFrame(master_frame4, height=32)
        slider_frame.pack(pady=5)
        color_button_and_color_entry_frame = ctk.CTkFrame(master_frame4, height=32)
        color_button_and_color_entry_frame.pack(fill='x', padx=5)
        toogle_state_button = ctk.CTkButton(master_frame4, text='Activate Color Editor', text_color='white', hover_color=self._set_color('white', 50), fg_color='black', command=lambda: self._toogle_color_editor_state(name))
        toogle_state_button.pack(side='bottom', fill='x', pady=5)
        
        slider1_frame = ctk.CTkFrame(slider_frame, height=32)
        slider1_frame.pack(pady=5)
        slider2_frame = ctk.CTkFrame(slider_frame, height=32)
        slider2_frame.pack(pady=2)
        slider3_frame = ctk.CTkFrame(slider_frame, height=32)
        slider3_frame.pack(pady=5)
        
        color_sliders = []
        
        key_strokes_binding_list = [
            lambda: self.root.bind('<Left>', lambda m: self.move_cursor(name, display_label, -1)),
            lambda: self.root.bind('<Right>', lambda m: self.move_cursor(name, display_label, 1)),
            lambda: self.root.bind('b', lambda m: self.backspace_text(name, display_label)),
            lambda: self.root.bind('(', lambda m: self.update_text(name, display_label, '(')),
            lambda: self.root.bind(')', lambda m: self.update_text(name, display_label, ')')),
            lambda: self.root.bind('<End>', lambda m: self.move_to_endings(name, display_label, 1)),
            lambda: self.root.bind('<Home>', lambda m: self.move_to_endings(name, display_label, -1)),
            lambda: self.root.bind('c', lambda m: self.clear_all(name, display_label)),
        ]
        
        self.initial_display_label = display_label = ctk.CTkLabel(sub_frame1, fg_color='transparent', text=self.cursor_char, anchor='w', font=ctk.CTkFont(size=20, weight='bold'))
        display_label.pack(side='left', fill='x', expand=True, padx=5)
        
        self.funtion_calcs_info[name].update({self.keystrokes_id: key_strokes_binding_list})
        self.funtion_calcs_info[name].update({self.color_sliders_id: color_sliders})
        
        def create_color_sliders(frame: ctk.CTkFrame, color_name: str):
            ctk.CTkLabel(frame, text=color_name).pack(side='left', padx=5)
            ctk.CTkLabel(frame, text='0').pack(side='left', padx=5)
            slider = ctk.CTkSlider(frame, from_=0, to=255, button_color=color_name.lower(), command=lambda trash: self._slider_color_update(name))
            slider.pack(side='left')
            ctk.CTkLabel(frame, text='255').pack(side='left', padx=5)
            color_sliders.append(slider)
        
        create_color_sliders(slider1_frame, 'Red')
        create_color_sliders(slider2_frame, 'Green')
        create_color_sliders(slider3_frame, 'Blue')
        
        color_entry = ctk.CTkEntry(color_button_and_color_entry_frame)
        color_entry.insert(0, "#ff0000")
        color_entry.pack(side='left', padx=10)
        color_button = ctk.CTkButton(color_button_and_color_entry_frame, text='', width=28, fg_color='red', hover=False)
        color_button.pack(side='right')
        
        self.funtion_calcs_info[name][self.color_editor_enables_id] = True
        self.funtion_calcs_info[name][self.color_entry_id] = color_entry
        self.funtion_calcs_info[name][self.color_button_id] = color_button
        self.funtion_calcs_info[name][self.color_entry_repr_id] = repr(self.root.focus_get())
        self.funtion_calcs_info[name][self.toogle_state_button_id] = toogle_state_button
        
        def update_focus():
            color_entry.focus_force()
            self.funtion_calcs_info[name][self.color_entry_repr_id] = repr(self.root.focus_get())
            self.root.focus()
        
        self.root.after(2000, update_focus)
        
        calculator_column1 = ctk.CTkFrame(master_frame2)
        calculator_column1.pack(pady=2, fill='both', expand=True)
        calculator_column2 = ctk.CTkFrame(master_frame2)
        calculator_column2.pack(pady=2, fill='both', expand=True)
        calculator_column3 = ctk.CTkFrame(master_frame2)
        calculator_column3.pack(pady=2, fill='both', expand=True)
        calculator_column4 = ctk.CTkFrame(master_frame2)
        calculator_column4.pack(pady=2, fill='both', expand=True)
        calculator_column5 = ctk.CTkFrame(master_frame2)
        calculator_column5.pack(pady=2, fill='both', expand=True)
        calculator_column6 = ctk.CTkFrame(master_frame2)
        calculator_column6.pack(pady=2, fill='both', expand=True)
        calculator_column7 = ctk.CTkFrame(master_frame2)
        calculator_column7.pack(pady=2, fill='both', expand=True)

        def update_text_name_func(func_name): return lambda: self.update_text(name, display_label, func_name + '(')
        
        special_operations_frame = ctk.CTkScrollableFrame(master_frame3, width=230)
        special_operations_frame.pack(fill='both', expand=True)
        
        row_amt = 2 # Increasing it will cause there to be function losses
        
        sosf_range = (len(self.math_func_strings) // row_amt) + (1 if (len(self.math_func_strings) % row_amt) != 0 else 0)
        special_operations_sub_frames = [ctk.CTkFrame(special_operations_frame) for i in range(sosf_range)]
        
        for func_name_index, func_name in enumerate(self.math_func_strings):
            ctk.CTkButton(special_operations_sub_frames[func_name_index % len(special_operations_sub_frames)], 100, text=func_name, command=update_text_name_func(func_name)).pack(side='left', fill='x', expand=True, padx=10, pady=5)
            
        for frames in special_operations_sub_frames:
            frames.pack(pady=2, expand=True, fill='x')
        
        self.make_generic_button(name, display_label, calculator_column1, key_strokes_binding_list, '7')
        self.make_generic_button(name, display_label, calculator_column1, key_strokes_binding_list, '8')
        self.make_generic_button(name, display_label, calculator_column1, key_strokes_binding_list, '9')
        self.make_generic_button(name, display_label, calculator_column1, key_strokes_binding_list, ' + ')
        
        self.make_generic_button(name, display_label, calculator_column2, key_strokes_binding_list, '6')
        self.make_generic_button(name, display_label, calculator_column2, key_strokes_binding_list, '5')
        self.make_generic_button(name, display_label, calculator_column2, key_strokes_binding_list, '4')
        self.make_generic_button(name, display_label, calculator_column2, key_strokes_binding_list, ' - ')
        
        self.make_generic_button(name, display_label, calculator_column3, key_strokes_binding_list, '3')
        self.make_generic_button(name, display_label, calculator_column3, key_strokes_binding_list, '2')
        self.make_generic_button(name, display_label, calculator_column3, key_strokes_binding_list, '1')
        self.make_generic_button(name, display_label, calculator_column3, key_strokes_binding_list, ' * ')
        
        self.make_generic_button(name, display_label, calculator_column4, key_strokes_binding_list, X)
        self.make_generic_button(name, display_label, calculator_column4, key_strokes_binding_list, '0')
        self.make_generic_button(name, display_label, calculator_column4, key_strokes_binding_list, '.')
        self.make_generic_button(name, display_label, calculator_column4, key_strokes_binding_list, ' / ')
        
        self.make_generic_button(name, display_label, calculator_column5, key_strokes_binding_list, '2', lambda: self.update_text(name, display_label, '`2'), font_size_increase=0.5)
        self.make_generic_button(name, display_label, calculator_column5, key_strokes_binding_list, '3', lambda: self.update_text(name, display_label, '`3'), font_size_increase=0.5)
        self.make_generic_button(name, display_label, calculator_column5, key_strokes_binding_list, '0.5', lambda: self.update_text(name, display_label, '`0.5'), font_size_increase=0.5)
        self.make_generic_button(name, display_label, calculator_column5, key_strokes_binding_list, 'x', lambda: self.update_text(name, display_label, '`'), font_size_increase=0.5)
        
        self.make_generic_button(name, display_label, calculator_column6, key_strokes_binding_list, '^')
        self.make_generic_button(name, display_label, calculator_column6, key_strokes_binding_list, '%')
        self.make_generic_button(name, display_label, calculator_column6, key_strokes_binding_list, '(')
        self.make_generic_button(name, display_label, calculator_column6, key_strokes_binding_list, ')')
        
        self.make_generic_button(name, display_label, calculator_column7, key_strokes_binding_list, 'Update', lambda: self.send_graph_info_func(self.compile_calculator_text(display_label._text), self.funtion_calcs_info[name][self.color_entry_id].get(), index))
        self.make_generic_button(name, display_label, calculator_column7, key_strokes_binding_list, 'Remove', lambda: self.remove_graph_info_func(self.funtion_calcs_info[name][self.index_id]))
        
        self._toogle_color_editor_state(name)
        self._slider_color_update(name)
    
    def _set_color(self, color: ColorType, opacity: int, hex_: bool = True):
        assert self._is_color(color), f'"{color}" is not a valid color'
        
        if isinstance(color, str):
            if '#' in color:
                color_tuple = [(math.fabs(255 - (col * 255)) / 255) for col in pygame.Color(color).cmy]
            else:
                color_tuple = [i/255 for i in pygame.colordict.THECOLORS[color]]
        elif isinstance(color, tuple | list | pygame.color.Color):
            color_tuple = [i/255 for i in color]
        elif isinstance(color, int):
            color_tuple = [i/255 for i in pygame.Color(color)]
        else:
            raise Exception('Invalid color argument')

        for i in color_tuple[:3]:
            black = i == 0
            if not black:
                break
        
        color = [255 - opacity for _ in color_tuple] if black else [i * opacity for i in color_tuple]
        
        if len(color) >= 4:
            color = color[:3]
        
        return self._rgb_to_hex(color) if hex_ else color
    
    def _rgb_to_hex(self, rgb):
        rgb = tuple(int(max(0, min(255, component))) for component in rgb)
        hex_color = "#{:02X}{:02X}{:02X}".format(*rgb)
        
        return hex_color
    
    def _is_color(self, color):
        try:
            pygame.colordict.THECOLORS[color]
        except:
            try:
                pygame.Color(color).cmy
            except:
                return False
            return True
        return True
    
    def _toogle_color_editor_state(self, name: str):
        info = self.funtion_calcs_info[name]
        
        color_reduc = 35
        
        if info[self.color_editor_enables_id]:
            for slider in info[self.color_sliders_id]:
                slider.configure(state='disabled', button_color=self._rgb_to_hex([max(0, v - color_reduc) for v in self._set_color(slider._button_color, 255, False)]))
            
            info[self.color_button_id].configure(state='disabled', fg_color=self._rgb_to_hex([max(0, v - color_reduc) for v in self._set_color(info[self.color_button_id]._fg_color, 255, False)]))
            info[self.color_entry_id].configure(state='disabled')
            info[self.toogle_state_button_id].configure(text='Activate Color Editor', text_color='white', hover_color=self._set_color('white', 50), fg_color='black')
            self.root.focus()
        else:
            for slider in info[self.color_sliders_id]:
                slider.configure(state='normal', button_color=self._rgb_to_hex([max(0, v + color_reduc) for v in self._set_color(slider._button_color, 255, False)]))
            info[self.color_button_id].configure(state='normal', fg_color=self._rgb_to_hex([min(255, v + color_reduc) for v in self._set_color(info[self.color_button_id]._fg_color, 255, False)]))
            info[self.color_entry_id].configure(state='normal')
            info[self.toogle_state_button_id].configure(text='Deactivate Color Editor', text_color='black', hover_color=self._set_color('black', 50), fg_color='white')
            info[self.color_entry_id].focus_force()
        info[self.color_editor_enables_id] = not info[self.color_editor_enables_id]
    
    def _slider_color_update(self, name: str):
        color_sliders = self.funtion_calcs_info[name][self.color_sliders_id]
        color_entry = self.funtion_calcs_info[name][self.color_entry_id]
        
        color_entry.delete(0, 'end')
        color_entry.insert(0, self._rgb_to_hex(list(slider.get() for slider in color_sliders)).lower())
        self._update_color(name, color_entry.get())
    
    def _update_color(self, name: str, color: ColorType):
        color = list(pygame.Color(color))[:3]
        color_sliders = self.funtion_calcs_info[name][self.color_sliders_id]
        color_button = self.funtion_calcs_info[name][self.color_button_id]
        
        for index, slider in enumerate(color_sliders):
            c = color.copy()
            c[index] = 255
            hex_color = self._rgb_to_hex(c)
            hex_new_hover_color = self._rgb_to_hex(self._set_color(c, 200, False))
            slider.configure(button_color=hex_color, button_hover_color=hex_new_hover_color)
        color_button.configure(fg_color=self._rgb_to_hex(color))#, hover_color=new_hover_color)
    
    def _update_colors_from_entry(self, name: str):
        f_info = self.funtion_calcs_info[name]
        if f_info[self.frame_id] == self.current_frame:
            color_sliders = f_info[self.color_sliders_id]
            color_entry = f_info[self.color_entry_id]
            entry_color = color_entry.get()
            
            if f_info[self.color_entry_repr_id] == repr(self.root.focus_get()):
                if self._is_color(entry_color):
                    color = self._set_color(entry_color, 255, False)
                    for slider_index, slider in enumerate(color_sliders):
                        slider.set(color[slider_index])
                    self._update_color(name, self._rgb_to_hex(color))
            color_entry.after(100, lambda: self._update_colors_from_entry(name))
    
    def _add_sub_calc(self, name, temporary):
        self.current_menu_bar_frame = ctk.CTkFrame(self.frame_menu_bar, height=self.frame_menu_bar._desired_height, fg_color='transparent')
        self.current_menu_bar_frame.pack(side='left', fill='x', expand=True)
        _make_set_func_func = lambda name: lambda: self.set_func_focus(name)
        
        ctk.CTkButton(self.current_menu_bar_frame,
                      text=name,
                      command=_make_set_func_func(name),
                      fg_color='transparent',
                      corner_radius=0).place(relx=0.5, rely=0.5, relwidth=1, relheight=1, anchor='center')
        
        if temporary:
            ctk.CTkButton(self.current_menu_bar_frame,
                          text='',
                          image=ctk.CTkImage(Image.open(r'images\cancel_icon.png'),
                                             size=(self.current_menu_bar_frame._desired_height // 4, self.current_menu_bar_frame._desired_height // 4)),
                          width=0,
                          height=0,
                          command=lambda: self.remove_function(name),
                          fg_color='transparent'
                        ).place(relx=1, rely=0, anchor='ne')
        
        self.current_frame = ctk.CTkFrame(self.bg_display_frame)
        self.current_frame.place(relx=0.5, rely=0.5, relwidth=1, relheight=1, anchor='center')
        self.funtion_calcs_info.update({name: {self.frame_id: self.current_frame, self.menu_bar_frame_id: self.current_menu_bar_frame, self.index_id: len(self.funtion_calcs_info), self.cursor_id: 0}})
        self._make_sub_calc(name)
        self.set_func_focus(name)
        
        self.menubar_bg_frame.lift()
    
    def add_sub_calc(self, temporary=True):
        self.funcs_amt += 1
        new_frame_name = f'Function {self.funcs_amt}'
        self._add_sub_calc(new_frame_name, temporary)
    
    def remove_function(self, name):
        main_frame = self.funtion_calcs_info[name][self.frame_id]
        keys = list(self.funtion_calcs_info.keys())
        index = keys.index(name)
        self.remove_graph_info_func(index)
        if self.current_frame == main_frame:
            self.set_func_focus(keys[index - 1])
        menu_frame_button_frame = self.funtion_calcs_info[name][self.menu_bar_frame_id]
        main_frame.destroy()
        menu_frame_button_frame.destroy()
        self.funtion_calcs_info.pop(name)
    
    def set_func_focus(self, name):
        for values in self.funtion_calcs_info.values():
            current_frame = values[self.frame_id]
            current_menu_bar_frame = values[self.menu_bar_frame_id]
            current_frame.place(relx=2, rely=2, anchor='nw')
            current_menu_bar_frame.configure(fg_color='transparent')
            for widg in current_menu_bar_frame.slaves():
                widg.configure(fg_color='transparent')
        self.current_frame = self.funtion_calcs_info[name][self.frame_id]
        self.current_menu_bar_frame = self.funtion_calcs_info[name][self.menu_bar_frame_id]
        keystroke_bindings = self.funtion_calcs_info[name][self.keystrokes_id]
        self.current_menu_bar_frame.configure(fg_color=ctk.ThemeManager.theme['CTkButton']['fg_color'])
        for widg in self.current_menu_bar_frame.slaves():
            widg.configure(fg_color=ctk.ThemeManager.theme['CTkButton']['fg_color'])
        self.current_frame.place(relx=0.5, rely=0.5, relwidth=1, relheight=1, anchor='center')
        for binding in keystroke_bindings:
            binding()
        self._update_colors_from_entry(name)
    
    def update_text(self, name: str, display_label: ctk.CTkLabel, text: str):
        if self.funtion_calcs_info[name][self.color_entry_repr_id] != repr(self.root.focus_get()):
            display_label.configure(text=display_label._text[:self.funtion_calcs_info[name][self.cursor_id]] + text + display_label._text[self.funtion_calcs_info[name][self.cursor_id]:])
            self.funtion_calcs_info[name][self.cursor_id] += len(text)
    
    def clear_all(self, name, display_label: ctk.CTkLabel):
        self.move_to_endings(name, display_label, 1)
        for _ in range(len(display_label._text)):
            self.backspace_text(name, display_label)
    
    def move_to_endings(self, name, display_label: ctk.CTkLabel, direction: Literal[-1, 1]):
        if direction > 0:
            for _ in range(len(display_label._text[self.funtion_calcs_info[name][self.cursor_id]:])):
                self.move_cursor(name, display_label, direction)
        elif direction < 0:
            for _ in range(len(display_label._text[:self.funtion_calcs_info[name][self.cursor_id]])):
                self.move_cursor(name, display_label, direction)
    
    def backspace_text(self, name: str, display_label: ctk.CTkLabel, skip_recurse: bool = False):
        if self.funtion_calcs_info[name][self.cursor_id] != 0:
            self.funtion_calcs_info[name][self.cursor_id] -= 1
            text = display_label._text.replace(self.cursor_char, '')
            display_label_text_list = list(text)
            display_label_text_list.pop(self.funtion_calcs_info[name][self.cursor_id])
            display_label_text_list.insert(self.funtion_calcs_info[name][self.cursor_id], self.cursor_char)
            new_text = ''.join(display_label_text_list)
            display_label.configure(text=new_text)
            there_was_a_space = False
            if not skip_recurse:
                if text[self.funtion_calcs_info[name][self.cursor_id]].isalpha() and text[self.funtion_calcs_info[name][self.cursor_id]] != X:
                    self.backspace_text(name, display_label)
                if text[self.funtion_calcs_info[name][self.cursor_id]].isspace():
                    there_was_a_space = True
                    self.backspace_text(name, display_label)
            if there_was_a_space:
                self.backspace_text(name, display_label, True)
    
    def move_cursor(self, name: str, display_label: ctk.CTkLabel, direction: Literal[-1, 1]):
        if (direction < 0 and self.funtion_calcs_info[name][self.cursor_id] != 0) or (direction > 0 and self.funtion_calcs_info[name][self.cursor_id] != len(display_label._text) - 1):
            init_text = list(display_label._text.replace(self.cursor_char, ''))
            self.funtion_calcs_info[name][self.cursor_id] += direction
            init_text.insert(self.funtion_calcs_info[name][self.cursor_id], self.cursor_char)
            text = ''.join(init_text)
            display_label.configure(text=text)
            if init_text[self.funtion_calcs_info[name][self.cursor_id]].isalpha():
                self.move_cursor(direction)
    
    def make_generic_button(self, name, display_label: ctk.CTkLabel, frame: ctk.CTkFrame, key_strokes_binding_list: list, text: str, func: Callable[[], None] | None = None, font_size_increase: int | None = None):
        constant_font_size_increase = 2
        
        font = ctk.CTkFont(size=int(ctk.ThemeManager.theme["CTkFont"]["size"] * constant_font_size_increase * (font_size_increase if font_size_increase is not None else 1)))
        ctk.CTkButton(frame, text=text, font=font, command=(lambda: self.update_text(name, display_label, text)) if func is None else func).pack(side='left', fill='both', expand=True, padx=10, pady=5)
        key_strokes_binding_list.append(lambda: self.root.bind(text, lambda m: self.update_text(name, display_label, text)))
    
    def compile_calculator_text(self, text: str):
        text = text.replace(self.cursor_char, '')
        text = text.replace('`', '**')
        
        maths_string_funcs = [self.math_func_strings[index] for _, index in sorted([(len(f_string), index) for index, f_string in enumerate(self.math_func_strings)], reverse=True)]
        
        for i, str_f in enumerate(maths_string_funcs):
            maths_string_funcs[i] = self._get_funcs_replacement_fmt(self.ascii_letters_without_x[self.math_func_strings.index(str_f)])
        
        for ir_name in maths_string_funcs:
            text = text.replace(self.math_func_strings_ir[ir_name], ir_name)
        
        text = text.replace(X, f'({X})')
        
        for func_index, func_name in enumerate(maths_string_funcs):
            text = text.replace(func_name, f'@{func_index}')
        
        indexes = []
        pou = 1
        ref_text = text
        
        for i, t in enumerate(text):
            if t == '@':
                if text[i - 1].isnumeric() and i != 0:
                    ref_text_list = list(ref_text)
                    ref_text_list.insert(i, ' * ')
                    ref_text = ''.join(ref_text_list)
                if text[i + 2].isnumeric():
                    pou = 2
                str_func_index = int(''.join(text[i + 1: i + pou + 1]))
                indexes.append(str_func_index)
                pou = 1
        
        for i in indexes:
            text = text.replace('@' + str(i), f'__import__("math").{maths_string_funcs[i]}')
        
        l_text = list(text)
        for i, t in enumerate(l_text):
            if t == '(':
                if i - 1 > -1:
                    if l_text[i - 1] in (')', ) or l_text[i - 1].isnumeric():
                        l_text.insert(i, ' * ')
            elif t == ')':
                if i + 1 < len(l_text):
                    if l_text[i + 1] in ('(', '_') or l_text[i + 1].isnumeric():
                        l_text.insert(i + 1, ' * ')
        text = ''.join(l_text)
        
        left_bracket_difference = text.count('(') - text.count(')')
        if left_bracket_difference > 0:
            text += ')' * left_bracket_difference
        
        for id_, name in self.math_func_strings_ir.items():
            text = text.replace(id_, name)
        
        return text
    
    def get_graph_func(self, text: str):
        return lambda x: eval(text.replace(X, str(x)))
    
    def loop(self):
        try:
            self.api_info = self.read_from_api()
        except FileNotFoundError:
            self.root.quit()
        
        if self.api_info[GRAPH_APP_INFO_ID][GRAPH_APP_CRAPH_CALC_CLOSE_ID]:
            self.root.quit()
        
        self.root.after(100, self.loop)
    
    def run(self):
        self.loop()
        self.root.mainloop()
        if Path(self.api_file).exists():
            self.api_info[GRAPH_CALC_INFO_ID][GRAPH_CALC_RUNNING_ID] = False
            self.write_to_api(self.api_info)

