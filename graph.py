
import os
from pathlib import Path
import sys
import math
import json
import threading
import time
from tkinter import dialog
from PIL import Image
from typing import Callable, Literal
import pygame
from misc_components import Button, APIObject
from settings import *



class Graph:
    def __init__(self,
                 screen: pygame.Surface,
                 graph_functions_info: list[tuple[Callable, ColorType]],
                 plot_accuracy: int,
                 grid_size: Number,
                 grid_line_number_accuracy: int,
                 min_plot_rangex: int,
                 max_plot_rangex: int,
                 min_plot_rangey: int,
                 max_plot_rangey: int,
                 grid_line_color: ColorType,
                 grid_text_color: ColorType,
                 accesories_color: ColorType,
                 base_line_width: Number,
                 x_scale: Number = 1,
                 y_scale: Number = 1):
        self.screen = screen
        self.grid_text_color = grid_text_color
        self.grid_line_color = grid_line_color
        self.accesories_color = accesories_color
        self.base_line_width = base_line_width
        self.plot_accuracy = plot_accuracy
        self.grid_size = grid_size
        self.grid_line_number_accuracy = grid_line_number_accuracy
        self.x_scale = x_scale
        self.y_scale = y_scale
        
        self.mid_scr_point_x = self.screen.get_width() / 2
        self.mid_scr_point_y = self.screen.get_height() / 2
        
        self.mid_scr_ref_x = self.mid_scr_point_x
        self.mid_scr_ref_y = self.mid_scr_point_y
        
        self.mouse_pos = (0, 0)
        self.draw_plot_start_ref = (0, 0)
        self.draw_plot_start_ref = (0, 0)
        
        self.font = pygame.font.SysFont('Cambria', 20)
        
        self.min_draw_area_x = 0
        self.min_draw_area_y = 0
        self.max_draw_area_x = self.screen.get_width()
        self.max_draw_area_y = self.screen.get_height()
        
        self.min_plot_rangex = int(min_plot_rangex * self.x_scale * self.grid_size)
        self.max_plot_rangex = int(max_plot_rangex * self.x_scale * self.grid_size)
        self.min_plot_rangey = int(min_plot_rangey * self.y_scale * self.grid_size)
        self.max_plot_rangey = int(max_plot_rangey * self.y_scale * self.grid_size)
        
        self.min_scr_x_val = (self.mid_scr_point_x * 2) + ((self.min_plot_rangex / self.plot_accuracy) * self.x_scale * self.grid_size)
        self.max_scr_x_val = (self.max_plot_rangex / self.plot_accuracy) * self.x_scale * self.grid_size
        self.min_scr_y_val = (self.mid_scr_point_y * 2) + ((self.min_plot_rangey / self.plot_accuracy) * self.y_scale * self.grid_size)
        self.max_scr_y_val = (self.max_plot_rangey / self.plot_accuracy) * self.y_scale * self.grid_size
        
        self.graph_functions_info = graph_functions_info
        
        self.graph_func_amt = len(self.graph_functions_info)
        
        self.plot_info = []
        self.plotted_points = []
        self.orig_plotted_points = []
        self.plot_points = []
        self.orig_plotted_points_tracker = []
        
        self.show_cordinates_hovered = False
        self._has_toogled_show_coordinate = False
        self.show_mouse_xy_cordinates = False
        self._has_toogled_show_graph_xy_coordinate = False
        self._has_plotted_it_there = False
        self.plot_it_here = False
        
        self.recalculate_everything = True
        self.recalculate_graph_line = False
        self.recalculate_text_and_gridlines = False
    
    def _sign(self, num: Number):
        return (num / abs(num)) if num != 0 else 1
    
    def _calculate_plot_vals(self, graph_info: list[Callable, ColorType], min_range: int, max_range: int):
        for i in range(min_range, max_range):
            try:
                x = i / self.plot_accuracy
                
                x_starting_plot = x * self.x_scale * self.grid_size
                x_ending_plot = (x - (1 / self.plot_accuracy)) * self.x_scale * self.grid_size
                
                for y, color in graph_info:
                    y_starting_plot = -(y(x) * self.y_scale * self.grid_size)
                    y_ending_plot = -(y(x - (1 / self.plot_accuracy)) * self.y_scale * self.grid_size)
                    
                    start_point = [x_starting_plot, y_starting_plot]
                    end_point = [x_ending_plot, y_ending_plot]
                    
                    self.plot_info.append([color, start_point, end_point, 4, 'plot line'])
            
            except (ValueError, ZeroDivisionError, OverflowError, TypeError):
                pass
    
    def _reposition_grid(self, min_range):
        for i in self.plot_info:
            if isinstance(i[0], pygame.Color | tuple | list | str):
                _, start, end, _, id_ = i
                if 'grid line' in id_:
                    d_X = end[0] - start[0]
                    d_Y = end[1] - start[1]
                    if start[1] != end[1]:
                        if 'x' in id_:
                            start[1] -= d_Y + (((min_range / self.plot_accuracy) * self.grid_size) * 2)
                            end[1] -= d_Y + (((min_range / self.plot_accuracy) * self.grid_size) * 2)
                    else:
                        if 'y' in id_:
                            start[0] += d_X + (((min_range / self.plot_accuracy) * self.grid_size) * 2)
                            end[0] += d_X + (((min_range / self.plot_accuracy) * self.grid_size) * 2)
    
    def _add_text_and_gridlines(self, min_rangex, max_rangex, min_rangey, max_rangey):
        max_end_of_graph_y = ((max_rangex * self.x_scale) / self.plot_accuracy) * self.grid_size
        min_end_of_graph_y = (min_rangex / self.plot_accuracy) * self.grid_size
        
        max_cut_off_rangex = (max_rangex * self.x_scale) / self.grid_size
        min_cut_off_rangex = (min_rangex * self.x_scale) / self.grid_size
        
        for i in range(min_rangex, max_rangex):
            x = i / self.plot_accuracy
            
            x_plot = x * self.x_scale * self.grid_size
            
            if min_cut_off_rangex < x < max_cut_off_rangex:
                if x != 0:
                    if (x / self.grid_line_number_accuracy).is_integer():
                        self.plot_info.append([self.grid_line_color, [x_plot, min_end_of_graph_y], [x_plot, max_end_of_graph_y], int(self.base_line_width / 2), 'grid linex'])
                        text = self.font.render(str(int(x)), False, self.grid_text_color)
                        self.plot_info.append((text, [x_plot - (text.get_width() / 2) + int(self.base_line_width / 2), 0], 'textx'))
                    elif (x / (self.grid_line_number_accuracy / 2)).is_integer():
                        self.plot_info.append([self.grid_line_color, [x_plot, min_end_of_graph_y], [x_plot, max_end_of_graph_y], max(int(self.base_line_width / 6), 1), 'grid linex'])
                else:
                    self.plot_info.append([self.grid_line_color, [x_plot, min_end_of_graph_y], [x_plot, max_end_of_graph_y], self.base_line_width, 'grid linex'])
        
        min_rangey = -max_rangey
        max_rangey = -min_rangey
        
        max_end_of_graph_x = (max_rangey / self.plot_accuracy) * self.grid_size
        min_end_of_graph_x = ((min_rangey * self.y_scale) / self.plot_accuracy) * self.grid_size
        
        max_cut_off_rangey = (max_rangey * self.y_scale) / self.grid_size
        min_cut_off_rangey = (min_rangey * self.y_scale) / self.grid_size
        
        for i in range(min_rangey, max_rangey):
            y = i / self.plot_accuracy
            
            y_plot = y * self.y_scale * self.grid_size
            
            if min_cut_off_rangey < y < max_cut_off_rangey:
                if y != 0:
                    if (y / self.grid_line_number_accuracy).is_integer():
                        self.plot_info.append([self.grid_line_color, [min_end_of_graph_x, y_plot], [max_end_of_graph_x , y_plot], int(self.base_line_width / 2), 'grid liney'])
                        text = self.font.render(str(int(-y)), False, self.grid_text_color)
                        self.plot_info.append((text, [0, y_plot - (text.get_height() / 2) + int(self.base_line_width / 2)], 'texty'))
                    elif (y / (self.grid_line_number_accuracy / 2)).is_integer():
                        self.plot_info.append([self.grid_line_color, [min_end_of_graph_x, y_plot], [max_end_of_graph_x, y_plot], max(int(self.base_line_width / 6), 1), 'grid liney'])
                else:
                    self.plot_info.append([self.grid_line_color, [min_end_of_graph_x, y_plot], [max_end_of_graph_x, y_plot], self.base_line_width, 'grid liney'])
    
    def _add_plotted_point(self):
        for orig_plot_point in self.orig_plotted_points:
            self._plot(*orig_plot_point)
        
        for blit_index in range(len(self.plot_points)):
            blit_point, color, x_thickness, x_half_length = self.plot_points[blit_index]
            criss = [color, [blit_point[0] - x_half_length, blit_point[1] - x_half_length], [blit_point[0] + x_half_length, blit_point[1] + x_half_length], x_thickness, 'plot line']
            self.plot_info.append(criss)
            cross = [color, [blit_point[0] + x_half_length, blit_point[1] - x_half_length], [blit_point[0] - x_half_length, blit_point[1] + x_half_length], x_thickness, 'plot line']
            self.plot_info.append(cross)
        
        self.plot_points = []
    
    def _update_mid_scr_pos(self, continue_moving_screen):
        if pygame.mouse.get_pressed()[0] and continue_moving_screen:
            self.mid_scr_point_x = self.mid_scr_rec_x + (self.mouse_pos[0] - self.mouse_pos_ref[0])
            self.mid_scr_point_y = self.mid_scr_rec_y + (self.mouse_pos[1] - self.mouse_pos_ref[1])
        else:
            self.mid_scr_rec_x = self.mid_scr_point_x
            self.mid_scr_rec_y = self.mid_scr_point_y
            self.mouse_pos_ref = self.mouse_pos
        
        self.mid_scr_point_x = pygame.math.clamp(self.mid_scr_point_x, self.min_scr_x_val, self.max_scr_x_val)
        self.mid_scr_point_y = pygame.math.clamp(self.mid_scr_point_y, self.min_scr_y_val, self.max_scr_y_val)
    
    def _update_ui(self):
        if self.keys[pygame.K_c]:
            if self._has_toogled_show_coordinate:
                self.show_cordinates_hovered = not self.show_cordinates_hovered
                self._has_toogled_show_coordinate = False
        else:
            self._has_toogled_show_coordinate = True
        
        if self.keys[pygame.K_p]:
            if self._has_toogled_show_graph_xy_coordinate:
                self.show_mouse_xy_cordinates = not self.show_mouse_xy_cordinates
                self._has_toogled_show_graph_xy_coordinate = False
        else:
            self._has_toogled_show_graph_xy_coordinate = True
        
        if self.keys[pygame.K_RETURN] and (self.show_mouse_xy_cordinates or self.show_cordinates_hovered):
            if self._has_plotted_it_there:
                self.plot_it_here = True
                self._has_plotted_it_there = False
        else:
            self._has_plotted_it_there = True
        
        x_coord = ((self.mouse_pos[0] - self.mid_scr_point_x) / self.grid_size) / self.x_scale
        y_coord = (-(self.mouse_pos[1] - self.mid_scr_point_y) / self.grid_size) / self.y_scale
        mouse_view_coordinate = x_coord, y_coord
        
        if self.show_cordinates_hovered:
            text_surf = self.font.render(str((mouse_view_coordinate[0], mouse_view_coordinate[1])), True, self.accesories_color)
            text_rect = pygame.Rect(self.mouse_pos[0] - text_surf.get_width(), self.mouse_pos[1] - text_surf.get_height(), *text_surf.get_size())
            self.screen.blit(text_surf, text_rect)
        
        if self.show_mouse_xy_cordinates:
            for graph_function, color in self.graph_functions_info:
                try:
                    x = self.mouse_pos[0]
                    y = self.mid_scr_point_y - (graph_function(mouse_view_coordinate[0]) * self.y_scale * self.grid_size)
                    text_surf = self.font.render(str((round(mouse_view_coordinate[0], 2), round((self.mid_scr_point_y - y) / (self.grid_size * self.y_scale), 2))), True, color)
                    line_rect = pygame.draw.line(self.screen, color, (x - 1, y - 1), (x - 1, self.mouse_pos[1] - 1), 4)
                    self.screen.blit(text_surf, line_rect.midright)
                    pygame.draw.circle(self.screen, color, (x, y), 5)
                except (ValueError, ZeroDivisionError, OverflowError, TypeError):
                    pass
            
            pygame.draw.circle(self.screen, self.accesories_color, self.mouse_pos, 5)
        
        if self.plot_it_here:
            if self.show_mouse_xy_cordinates:
                for index in range(len(self.graph_functions_info)):
                    self.plot_y(mouse_view_coordinate[0], index, 4, 8)
            elif self.show_cordinates_hovered:
                self.plot(mouse_view_coordinate, self.grid_line_color, 4, 8)
            self.recalculate_everything = True
            self.plot_it_here = False
    
    def _draw_grid(self):
        for i in self.plot_info:
            if isinstance(i[0], pygame.Color | tuple | list | str):
                color, start, end, width, id_ = i
                if 'x' in id_:
                    if 0 < start[0].real + self.mid_scr_point_x < self.screen.get_width() or 0 < end[0].real + self.mid_scr_point_x < self.screen.get_width():
                        pygame.draw.line(self.screen, color, (start[0].real + self.mid_scr_point_x, 0), (end[0].real + self.mid_scr_point_x, self.screen.get_height()), width)
                elif 'y' in id_:
                    if 0 < start[1].real + self.mid_scr_point_y < self.screen.get_height() or 0 < end[1].real + self.mid_scr_point_y < self.screen.get_height():
                        pygame.draw.line(self.screen, color, (0, start[1].real + self.mid_scr_point_y), (self.screen.get_width(), end[1].real + self.mid_scr_point_y), width)
                else:
                    if 0 < start[0].real + self.mid_scr_point_x < self.screen.get_width() or 0 < end[0].real + self.mid_scr_point_x < self.screen.get_width() and 0 < start[1].real + self.mid_scr_point_y < self.screen.get_height() or 0 < end[1].real + self.mid_scr_point_y < self.screen.get_height():
                        pygame.draw.line(self.screen, color, (start[0].real + self.mid_scr_point_x, start[1].real + self.mid_scr_point_y), (end[0].real + self.mid_scr_point_x, end[1].real + self.mid_scr_point_y), width)
            else:
                surf, pos, _ = i
                if 0 < pos[0].real + self.mid_scr_point_x < self.screen.get_width() and 0 < pos[1].real + self.mid_scr_point_y < self.screen.get_height():
                    self.screen.blit(surf, (pos[0].real + self.mid_scr_point_x, pos[1].real + self.mid_scr_point_y))
    
    def _plot(self, coord: tuple[float, float], color: ColorType, x_thickness: float, x_half_length: float):
        x, y = coord
        
        x_plot = x * self.x_scale * self.grid_size
        y_plot = -y * self.y_scale * self.grid_size
        
        point = x_plot, y_plot
        self.plot_points.append((point, color, x_thickness, x_half_length))
        self.recalculate_everything = True
    
    def configure(self, **kwargs):
        if 'graph_functions_info' in kwargs:
            graph_functions_info = kwargs.get('graph_functions_info')
            if graph_functions_info is not None:
                self.recalculate_everything = True
                self.graph_functions_info = graph_functions_info
        
        if 'plot_accuracy' in kwargs:
            plot_accuracy = kwargs.get('plot_accuracy')
            if plot_accuracy is not None:
                self.recalculate_everything = True
                self.plot_accuracy = plot_accuracy
        
        if 'grid_size' in kwargs:
            grid_size = kwargs.get('grid_size')
            if grid_size is not None:
                self.recalculate_everything = True
                self.grid_size = grid_size
        
        if 'grid_line_number_accuracy' in kwargs:
            grid_line_number_accuracy = kwargs.get('grid_line_number_accuracy')
            if grid_line_number_accuracy is not None:
                self.recalculate_text_and_gridlines = True
                self.grid_line_number_accuracy = grid_line_number_accuracy
        
        if 'min_plot_rangex' in kwargs:
            min_plot_rangex = kwargs.get('min_plot_rangex')
            if min_plot_rangex is not None:
                self.recalculate_everything = True
                self.min_plot_rangex = int(min_plot_rangex * self.x_scale * self.grid_size)
                self.min_scr_x_val = (self.mid_scr_point_x * 2) + ((self.min_plot_rangex / self.plot_accuracy) * self.x_scale * self.grid_size)
        
        if 'max_plot_rangex' in kwargs:
            max_plot_rangex = kwargs.get('max_plot_rangex')
            if max_plot_rangex is not None:
                self.recalculate_everything = True
                self.max_plot_rangex = int(max_plot_rangex * self.x_scale * self.grid_size)
                self.max_scr_x_val = (self.max_plot_rangex / self.plot_accuracy) * self.x_scale * self.grid_size
        
        if 'min_plot_rangey' in kwargs:
            min_plot_rangey = kwargs.get('min_plot_rangey')
            if min_plot_rangey is not None:
                self.recalculate_everything = True
                self.min_plot_rangey = int(min_plot_rangey * self.x_scale * self.grid_size)
                self.min_scr_y_val = (self.mid_scr_point_y * 2) + ((self.min_plot_rangey / self.plot_accuracy) * self.y_scale * self.grid_size)
        
        if 'max_plot_rangey' in kwargs:
            max_plot_rangey = kwargs.get('max_plot_rangey')
            if max_plot_rangey is not None:
                self.recalculate_everything = True
                self.max_plot_rangey = int(max_plot_rangey * self.x_scale * self.grid_size)
                self.max_scr_y_val = (self.max_plot_rangey / self.plot_accuracy) * self.y_scale * self.grid_size
        
        if 'grid_line_color' in kwargs:
            grid_line_color = kwargs.get('grid_line_color')
            if grid_line_color is not None:
                self.recalculate_text_and_gridlines = True
                self.grid_line_color = grid_line_color
        
        if 'grid_text_color' in kwargs:
            grid_text_color = kwargs.get('grid_text_color')
            if grid_text_color is not None:
                self.recalculate_text_and_gridlines = True
                self.grid_text_color = grid_text_color
        
        if 'accesories_color' in kwargs:
            accesories_color = kwargs.pop('accesories_color')
            if accesories_color is not None:
                self.recalculate_text_and_gridlines = True
                self.accesories_color = accesories_color
        
        if 'base_line_width' in kwargs:
            base_line_width = kwargs.pop('base_line_width')
            if base_line_width is not None:
                self.recalculate_text_and_gridlines = True
                self.base_line_width = base_line_width
        
        if 'x_scale' in kwargs:
            x_scale = kwargs.pop('x_scale')
            if x_scale is not None:
                self.recalculate_everything = True
                self.x_scale = x_scale
        
        if 'y_scale' in kwargs:
            y_scale = kwargs.pop('y_scale')
            if y_scale is not None:
                self.recalculate_everything = True
                self.y_scale = y_scale
    
    def add_y_func(self, func: Callable[[float], float], color: ColorType):
        self.recalculate_everything = True
        self.graph_functions_info.append([func, color])
     
    def plot(self, coord: tuple[float, float], color: ColorType, x_thickness: float = 2, x_half_length: float = 4):
        self.orig_plotted_points.append((coord, color, x_thickness, x_half_length))
    
    def plot_y(self, x: float, graphfuncindex: int, x_thickness: float = 2, x_half_length: float = 4):
        graph_func, color = self.graph_functions_info[graphfuncindex]
        y = graph_func(x)
        self.plot((x, y), color, x_thickness, x_half_length)
    
    def update(self, continue_moving_screen: bool = True):
        self.mouse_pos = pygame.mouse.get_pos()
        self.keys = pygame.key.get_pressed()
        
        if self.recalculate_everything:
            self.plot_info = []
            self._add_text_and_gridlines(self.min_plot_rangex, self.max_plot_rangex, self.min_plot_rangey, self.max_plot_rangey)
            self._calculate_plot_vals(self.graph_functions_info, max(self.min_plot_rangex, self.min_plot_rangey), min(self.max_plot_rangex, self.max_plot_rangey))
            self._add_plotted_point()
            self._reposition_grid(self.min_plot_rangex)
            
            self.orig_plotted_points_tracker = self.orig_plotted_points
            self.recalculate_everything = False
        else:
            if self.orig_plotted_points_tracker != self.orig_plotted_points:
                self._add_plotted_point()
                self.orig_plotted_points_tracker = self.orig_plotted_points
            if self.recalculate_graph_line:
                for graph_function, color in self.graph_functions_info:
                    self._calculate_plot_vals(graph_function, max(self.min_plot_rangex, self.min_plot_rangey), min(self.max_plot_rangex, self.max_plot_rangey), color)
                self.recalculate_graph_line = False
            if self.recalculate_text_and_gridlines:
                self._add_text_and_gridlines(self.min_plot_rangex, self.max_plot_rangex, self.min_plot_rangey, self.max_plot_rangey)
                self.recalculate_text_and_gridlines = False
        
        self._update_mid_scr_pos(continue_moving_screen)
        
        self._update_ui()
        
        self._draw_grid()

class GraphApp(APIObject):
    def __init__(self, api_file: FileType, open_calculator_func: Callable[[], None]):
        super().__init__(api_file)
        
        pygame.init()
        self.screen = pygame.display.set_mode((SCR_WIDTH, SCR_HEIGHT))
        pygame.display.set_caption('Graph Viewer')
        self.clock = pygame.time.Clock()

        self.functions_tracker = []
        self.calculator_open = True
        self.font = pygame.font.SysFont('Arial', 20)
        self.toogle_calc_state_thread = threading.Thread()
        
        self.api_file = api_file
        self.open_calculator_func = open_calculator_func
        
        self.graph = Graph(self.screen,
                           x_scale = 1,
                           y_scale = 1,
                           grid_size = 10,
                           plot_accuracy = 20,
                           base_line_width = 4,
                           max_plot_rangex = 100,
                           max_plot_rangey = 100,
                           min_plot_rangey = -100,
                           min_plot_rangex = -100,
                           accesories_color = 'red',
                           graph_functions_info = [],
                           grid_line_color = 'green',
                           grid_text_color = 'white',
                           grid_line_number_accuracy = 10,
                           )
        
        self.toogle_calculator_button = Button(self.screen, (20, 20), 'limegreen', (200, 30), image=self.font.render('Close Func Calculator', True, 'Black'), on_left_mouse_button_clicked=self._toogle_calculator_state)
    
    def _toogle_calculator_state(self):
        if self.calculator_open:
            self.api_info[GRAPH_APP_INFO_ID][GRAPH_APP_CRAPH_CALC_CLOSE_ID] = True
            self.write_to_api(self.api_info)
            self.toogle_calculator_button.configure(image=self.font.render('Open Func Calculator', True, 'Black'))
            self.calculator_open = False
        else:
            self.open_calculator_func()
            self.api_info[GRAPH_CALC_INFO_ID][GRAPH_CALC_RUNNING_ID] = True
            self.api_info[GRAPH_APP_INFO_ID][GRAPH_APP_CRAPH_CALC_CLOSE_ID] = False
            self.write_to_api(self.api_info)
            self.toogle_calculator_button.configure(image=self.font.render('Close Func Calculator', True, 'Black'))
            self.calculator_open = True
    
    def event_loop(self, event):
        self.keys = pygame.key.get_pressed()
        if event.type == pygame.QUIT:
            self.quit()

    def quit(self):
        if Path(self.api_file).exists():
            os.remove(self.api_file)
        pygame.quit()
        sys.exit()
        
    def app_loop(self):
        font_surf = self.font.render(f'FPS: {int(self.clock.get_fps())}', True, 'white')
        topleft = self.screen.get_width() - font_surf.get_width(), self.screen.get_height() - font_surf.get_height()
        self.screen.blit(font_surf, topleft)
        
        if not Path(self.api_file).exists():
            self.quit()
        
        self.api_info = self.read_from_api()
        
        func_strings = self.api_info[FUNC_INFO_ID]
        if self.functions_tracker != func_strings:
            def make_func(s):
                def func(x):
                    try:
                        return eval(s.replace(f'({X})', f'({x})'))
                    except:
                        return
                return func
            self.functions = [(make_func(s), color) for s, color in func_strings]
            self.graph.configure(graph_functions_info=self.functions)
            self.functions_tracker = func_strings
        if not self.api_info[GRAPH_CALC_INFO_ID][GRAPH_CALC_RUNNING_ID] and self.calculator_open:
            self._toogle_calculator_state()
        
        self.graph.update()
        self.toogle_calculator_button.update()
    
    def run(self):
        while True:
            self.delta_time = self.clock.tick(FPS)
            self.screen.fill(SCREEN_BG_COLOR)
            
            for event in pygame.event.get():
                self.event_loop(event)
            
            self.app_loop()
            
            pygame.display.update()


