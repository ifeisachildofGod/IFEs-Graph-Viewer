import math
import json
import pygame
from typing import Callable
from settings import *


class Button:
    def __init__(self,
                 screen: pygame.Surface,
                 pos: tuple,
                 bg_color: ColorType,
                 size: tuple,
                 on_hover: Callable = None,
                 on_not_hover: Callable = None,
                 on_left_mouse_button_clicked: Callable = None,
                 on_right_mouse_button_clicked: Callable = None,
                 on_not_left_mouse_button_clicked: Callable = None,
                 on_not_right_mouse_button_clicked: Callable = None,
                 many_actions_one_click: bool = False,
                 border_radius: int = 4,
                 on_hover_shade_val: float = 150,
                 on_click_shade_val: float = 200,
                 image: pygame.Surface = None,
                 scale_img: bool = False,
                 img_offset: int = 0,
                 invisible: bool = False) -> None:
        
        self.pos = pos
        self.size = size
        self.screen = screen
        self.on_hover = on_hover
        self.bg_color = bg_color
        self.scale_img = scale_img
        self.invisible = invisible
        self.img_offset = img_offset
        self.on_not_hover = on_not_hover
        self.border_radius = border_radius
        self.img_surf = self.image = image
        self.on_hover_shade_val = on_hover_shade_val
        self.on_click_shade_val = on_click_shade_val
        self.many_actions_one_click = many_actions_one_click
        self.on_left_mouse_button_clicked = on_left_mouse_button_clicked
        self.on_right_mouse_button_clicked = on_right_mouse_button_clicked
        self.on_not_left_mouse_button_clicked = on_not_left_mouse_button_clicked
        self.on_not_right_mouse_button_clicked = on_not_right_mouse_button_clicked
        
        self.disabled = False
        self.left_mouse_clicked = False
        self.right_mouse_clicked = False
        self.start_left_click_check = True
        self.start_right_click_check = True
        self.start_playing_hover_sound = True
        self.left_mouse_clicked_outside = True
        self.right_mouse_clicked_outside = True
        
        self.curr_button_opacity = 255
        self.SCR_WIDTH, self.SCR_HEIGHT = self.screen.get_size()
        self.widg_base_rect = pygame.Rect(*self.pos, *self.size)
        
        if self.image is not None:
            if self.scale_img:
                self.img_surf = pygame.transform.scale(self.image, (self.size[0] - self.img_offset, self.size[1] - self.img_offset))
            self.img_rect = self.img_surf.get_rect(center=self.widg_base_rect.center)
        else:
            self.img_surf = None
    
    def copy(self):
        return Button(screen = self.screen,
                      pos = self.pos,
                      bg_color = self.bg_color,
                      size = self.size,
                      on_hover = self.on_hover,
                      on_not_hover = self.on_not_hover,
                      on_left_mouse_button_clicked = self.on_left_mouse_button_clicked,
                      on_right_mouse_button_clicked = self.on_right_mouse_button_clicked,
                      on_not_left_mouse_button_clicked = self.on_not_left_mouse_button_clicked,
                      on_not_right_mouse_button_clicked = self.on_not_right_mouse_button_clicked,
                      many_actions_one_click = self.many_actions_one_click,
                      border_radius = self.border_radius,
                      image = self.image,
                      scale_img = self.scale_img,
                      img_offset = self.img_offset,
                      invisible = self.invisible)
    
    def set_pos(self, **kwargs):
        pos = (0, 0)
        total_rect = self.get_total_widget_rect()
        if kwargs:
            args = ['topleft', 'topright',
                    'bottomleft', 'bottomright',
                    'midleft', 'midright',
                    'midtop', 'midbottom',
                    'center', 'centerx', 'centery',
                    'left', 'right',
                    'top', 'bottom',
                    'x', 'y']
            pos = None
            for a in args:
                dest_pos = kwargs.get(a)
                if dest_pos:
                    if a in ('x', 'left'):
                        pos = dest_pos, self.pos[1]
                    elif a in ('y', 'top'):
                        pos = self.pos[0], dest_pos
                    elif a == 'right':
                        pos = dest_pos - total_rect.width, self.pos[1]
                    elif a == 'bottom':
                        pos = self.pos[0], dest_pos - total_rect.height
                    elif a == 'centerx':
                        pos = dest_pos - (total_rect.width / 2), self.pos[1]
                    elif a == 'centery':
                        pos = self.pos[0], dest_pos - (total_rect.height / 2)
                    elif a == 'topleft':
                        pos = dest_pos
                    elif a == 'topright':
                        pos = dest_pos[0] - total_rect.width, dest_pos[1]
                    elif a == 'bottomleft':
                        pos = dest_pos[0], dest_pos[1] - total_rect.height
                    elif a == 'bottomright':
                        pos = dest_pos[0] - total_rect.width, dest_pos[1] - total_rect.height
                    elif a == 'midleft':
                        pos = dest_pos[0], dest_pos[1] - (total_rect.height / 2)
                    elif a == 'midright':
                        pos = dest_pos[0] - total_rect.width, dest_pos[1] - (total_rect.height / 2)
                    elif a == 'midtop':
                        pos = dest_pos[0] - (total_rect.width / 2), dest_pos[1]
                    elif a == 'midbottom':
                        pos = dest_pos[0] - (total_rect.width / 2), dest_pos[1] - total_rect.height
                    elif a == 'center':
                        pos = dest_pos[0] - (total_rect.width / 2), dest_pos[1] - (total_rect.height / 2)
                    break
            if pos == None:
                raise TypeError(f'Invalid keyword argument passed: ({tuple(kwargs)})')
        if pos != self.pos:
            self.pos = pos
            self._set_topleft(self.pos)
    
    def configure(self, **kwargs):
        if 'bg_color' in kwargs:
            bg_color = kwargs.get('bg_color')
            if bg_color is not None:
                self.bg_color = bg_color
        
        if 'size' in kwargs:
            size = kwargs.get('size')
            if size is not None:
                self.size = size
                self.widg_base_rect.size = self.size
        
        if 'on_hover' in kwargs:
            on_hover = kwargs.get('on_hover')
            if on_hover is not None:
                self.on_hover = on_hover
        
        if 'on_not_hover' in kwargs:
            on_not_hover = kwargs.get('on_not_hover')
            if on_not_hover is not None:
                self.on_not_hover = on_not_hover
        
        if 'on_left_mouse_button_clicked' in kwargs:
            on_left_mouse_button_clicked = kwargs.get('on_left_mouse_button_clicked')
            if on_left_mouse_button_clicked is not None:
                self.on_left_mouse_button_clicked = on_left_mouse_button_clicked
        
        if 'on_right_mouse_button_clicked' in kwargs:
            on_right_mouse_button_clicked = kwargs.get('on_right_mouse_button_clicked')
            if on_right_mouse_button_clicked is not None:
                self.on_right_mouse_button_clicked = on_right_mouse_button_clicked
        
        if 'on_not_left_mouse_button_clicked' in kwargs:
            on_not_left_mouse_button_clicked = kwargs.get('on_not_left_mouse_button_clicked')
            if on_not_left_mouse_button_clicked is not None:
                self.on_not_left_mouse_button_clicked = on_not_left_mouse_button_clicked
        
        if 'on_not_right_mouse_button_clicked' in kwargs:
            on_not_right_mouse_button_clicked = kwargs.get('on_not_right_mouse_button_clicked')
            if on_not_right_mouse_button_clicked is not None:
                self.on_not_right_mouse_button_clicked = on_not_right_mouse_button_clicked
        
        if 'many_actions_one_click' in kwargs:
            many_actions_one_click = kwargs.get('many_actions_one_click')
            if many_actions_one_click is not None:
                self.many_actions_one_click = many_actions_one_click
        
        if 'on_hover_shade_val' in kwargs:
            on_hover_shade_val = kwargs.get('on_hover_shade_val')
            if on_hover_shade_val is not None:
                self.on_hover_shade_val = on_hover_shade_val
        
        if 'on_click_shade_val' in kwargs:
            on_click_shade_val = kwargs.get('on_click_shade_val')
            if on_click_shade_val is not None:
                self.on_click_shade_val = on_click_shade_val
        
        if 'border_radius' in kwargs:
            border_radius = kwargs.get('border_radius')
            if border_radius is not None:
                self.border_radius = border_radius
        
        if 'img_offset' in kwargs:
            img_offset = kwargs.get('img_offset')
            if img_offset is not None:
                self.img_offset = img_offset
                self.img_surf = pygame.transform.scale(self.image, (self.size[0] - self.img_offset, self.size[1] - self.img_offset))
                self.img_rect = self.img_surf.get_rect(center=self.widg_base_rect.center)
        
        if 'image' in kwargs:
            image = kwargs.get('image')
            if image is not None:
                self.img_surf = self.image = image
                if self.scale_img:
                    self.img_surf = pygame.transform.scale(self.image, (self.size[0] - self.img_offset, self.size[1] - self.img_offset))
                self.img_rect = self.img_surf.get_rect(center=self.widg_base_rect.center)
        
        if 'scale_img' in kwargs:
            scale_img = kwargs.get('scale_img')
            if scale_img is not None:
                self.scale_img = scale_img
                if self.scale_img:
                    self.img_surf = pygame.transform.scale(self.image, (self.size[0] - self.img_offset, self.size[1] - self.img_offset))
                    self.img_rect = self.img_surf.get_rect(center=self.widg_base_rect.center)
        
        if 'invisible' in kwargs:
            invisible = kwargs.get('invisible')
            if invisible is not None:
                self.invisible = invisible
    
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
        
        return color
    
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
    
    def _set_topleft(self, pos):
        self.widg_base_rect.topleft = pos
        if self.img_surf is not None:
            self.img_rect.center = self.widg_base_rect.center
    
    def _on_hover(self, action_performed):
        self.curr_button_opacity = self.on_hover_shade_val
        if action_performed is not None:
            action_performed()
    
    def _isclicked(self,
                   mouse_rect: pygame.Rect,
                   target: pygame.Rect,
                   left_mouse_clicked: bool,
                   right_mouse_clicked: bool,
                   hover_func: Callable,
                   not_hover_func: Callable,
                   left_click_func: Callable,
                   right_click_func: Callable,
                   left_not_clicked_func: Callable,
                   right_not_clicked_func: Callable):
        mouse_collission = mouse_rect.colliderect(target)
        
        if mouse_collission:
            hover_func()
        else:
            not_hover_func()
        
        if left_mouse_clicked and mouse_collission:
            self.left_mouse_clicked = True
        if not left_mouse_clicked:
            self.left_mouse_clicked = False

        if not self.left_mouse_clicked and not mouse_collission:
            self.left_mouse_clicked_outside = False
        if not left_mouse_clicked:
            self.left_mouse_clicked_outside = True
        
        if right_mouse_clicked and mouse_collission:
            self.right_mouse_clicked = True
        if not right_mouse_clicked:
            self.right_mouse_clicked = False

        if not self.right_mouse_clicked and not mouse_collission:
            self.right_mouse_clicked_outside = False
        if not right_mouse_clicked:
            self.right_mouse_clicked_outside = True
        
        left_mouse_clicked = self.left_mouse_clicked and self.left_mouse_clicked_outside
        right_mouse_clicked = self.right_mouse_clicked and self.right_mouse_clicked_outside

        if left_mouse_clicked:
            left_click_func()
        else:
            left_not_clicked_func()
        
        if right_mouse_clicked:
            right_click_func()
        else:
            right_not_clicked_func()
        
        return left_mouse_clicked, right_mouse_clicked, mouse_collission
    
    def _clicking(self, click_call_info: tuple[str, Callable], many_actions_one_click: bool = False):
        call_type, call_func = click_call_info
        match call_type:
            case 'on right clicked':
                self.curr_button_opacity = self.on_click_shade_val
                if self.start_right_click_check:
                    if call_func:
                        call_func()
                    self.start_right_click_check = False
                    self.start_right_click_check = self.start_right_click_check or many_actions_one_click
            case 'on left clicked':
                self.curr_button_opacity = self.on_click_shade_val
                if self.start_left_click_check:
                    if call_func:
                        call_func()
                    self.start_left_click_check = False
                    self.start_left_click_check = self.start_left_click_check or many_actions_one_click
            case 'on not left clicked':
                self.start_left_click_check = True
                if call_func:
                    call_func()
            case 'on not right clicked':
                self.start_right_click_check = True
                if call_func:
                    call_func()
            case 'on not hovering':
                self.curr_button_opacity = 255 if not self.disabled else 125
                if call_func:
                    call_func()
    
    def _draw(self):
        if not self.invisible:
            pygame.draw.rect(self.screen, self._set_color(self.bg_color, self.curr_button_opacity), self.widg_base_rect, 0, self.border_radius)
        if self.img_surf is not None:
            self.screen.blit(self.img_surf, self.img_rect)
    
    def update(self):
        clicked_info = []
        if not self.disabled:
            mouse_rect = pygame.Rect(*pygame.mouse.get_pos(), 1, 1)
            left_mouse_clicked = pygame.mouse.get_pressed()[0]
            right_mouse_clicked = pygame.mouse.get_pressed()[2]
            
            clicked_info = self._isclicked( mouse_rect,
                                            self.widg_base_rect,
                                            left_mouse_clicked,
                                            right_mouse_clicked,
                                            hover_func              =  lambda: self._on_hover(self.on_hover),
                                            not_hover_func          =  lambda: self._clicking(click_call_info=('on not hovering', self.on_not_hover)),
                                            left_click_func         =  lambda: self._clicking(click_call_info=('on left clicked', self.on_left_mouse_button_clicked), many_actions_one_click=self.many_actions_one_click),
                                            right_click_func        =  lambda: self._clicking(click_call_info=('on right clicked', self.on_right_mouse_button_clicked)),
                                            left_not_clicked_func   =  lambda: self._clicking(click_call_info=('on not left clicked', self.on_not_left_mouse_button_clicked)),
                                            right_not_clicked_func  =  lambda: self._clicking(click_call_info=('on not right clicked', self.on_not_right_mouse_button_clicked)),
                            )
        self._draw()
        
        return clicked_info


class APIObject:
    def __init__(self, api_file):
        self.api_file = api_file
        self.api_info = self.read_from_api()
    
    def write_to_api(self, info: dict):
        with open(self.api_file, "w") as file:
            file.write(json.dumps(info, indent=2))
    
    def read_from_api(self):
        try:
            with open(self.api_file) as file:
                return json.loads(file.read())
        except json.JSONDecodeError:
            return DEFAULT_API_STATE




