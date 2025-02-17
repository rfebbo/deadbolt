from hero import Hero
from item import Item 

import json
import os

import matplotlib.pyplot as plt

import pygame_widgets
from pygame_widgets.slider import Slider
from pygame_widgets.textbox import TextBox
import sys
from pygame.locals import *
import pygame as pg
import numpy as np

def load_dl_data():
    heroes = json.load(open('./data/processed/heroes.json', 'r'))
    items = json.load(open('./data/processed/items.json', 'r'))
    item_bonuses = json.load(open('./data/processed/item_bonuses.json', 'r'))
    level_bonuses = json.load(open('./data/processed/level_bonuses.json', 'r'))
    return heroes, items, item_bonuses, level_bonuses

def fill(surface, color):
    """Fill all pixels of the surface with color, preserve transparency."""
    w, h = surface.get_size()
    r, g, b, _ = color
    for x in range(w):
        for y in range(h):
            a = surface.get_at((x, y))[3]
            surface.set_at((x, y), pg.Color(r, g, b, a))

def get_avg_color(surface):
    """Get the average color of a surface."""
    w, h = surface.get_size()
    r, g, b = 0, 0, 0
    for x in range(w):
        for y in range(h):
            color = surface.get_at((x, y))
            if color.a <= 10:
                continue
            r += color.r
            g += color.g
            b += color.b

    r //= (w * h)
    g //= (w * h)
    b //= (w * h)

    return (r, g, b)

def load_mm_images(icon_size):
    mm_images = []
    mm_names = []
    h_colors = []
    for f in os.listdir('./mm_images'):
        mm_names.append(f)
        img = pg.image.load('./mm_images/'+f).convert_alpha()
        img = pg.transform.scale(img, (icon_size,icon_size))
        greyed_img = img.copy()
        fill(greyed_img, (100,100,100,255))
        
        mm_images.append((img, greyed_img))
        h_colors.append(get_avg_color(img))

    return mm_images, mm_names, h_colors

def add_hero_mm_images(heroes, icon_size):
    mm_images, mm_names, h_colors = load_mm_images(icon_size)
    for h in heroes:
        heroes[h]['enabled'] = False
        img_found = False
        for mmi, mmn, hc in zip(mm_images, mm_names, h_colors):
            if heroes[h]['name'][5:] in mmn:
                heroes[h]['icon'] = mmi[0]
                heroes[h]['greyed icon'] = mmi[1]
                heroes[h]['color'] = hc
                img_found = True
    
        if not img_found:
            print('no image found for ', heroes[h]['name'][5:])


def world_to_px(world_pos, world_size, screen_size):
    """Convert world coordinates to pixel coordinates."""
    world_x, world_y = world_pos
    world_width, world_height = world_size
    screen_width, screen_height = screen_size


    px_x = int((world_x / world_width) * screen_width)
    px_y = screen_height - int((world_y / world_height) * screen_height)

    return (px_x, px_y)

def draw_world_line(screen, world_pos1, world_pos2, world_size, screen_size, color):
    """Draw a line between two world coordinates on the screen."""
    px_pos1 = world_to_px(world_pos1, world_size, screen_size)
    px_pos2 = world_to_px(world_pos2, world_size, screen_size)

    pg.draw.line(screen, color, px_pos1, px_pos2, 5)

def draw_world_lines(screen, lines, world_size, screen_size, color):
    for wp1, wp2 in lines:
        px_pos1 = world_to_px(wp1, world_size, screen_size)
        px_pos2 = world_to_px(wp2, world_size, screen_size)
        pg.draw.line(screen, color, px_pos1, px_pos2, 5)

def draw_hero_portraits(heroes, screen, icon_size):
    for i, h in enumerate(heroes):
        if heroes[h]['enabled']:
            img = heroes[h]['icon']
        else:
            img = heroes[h]['greyed icon']
        
        hi = screen.blit(img, (i*icon_size,0))
        heroes[h]['icon_rect'] = hi

def draw_hero_lines(screen, heroes, world_size, window_size):
    for h in heroes:
        if heroes[h]['enabled']:
            start_x = 300
            start_y = 30
            last_dps = heroes[h]['dps_per_soul'][0]
            res = 10
            dps_scale = 400
            lines = set()
            
            for i, dps in enumerate(heroes[h]['dps_per_soul'][1:None:res]):
                sy = (last_dps * dps_scale) + start_y
                sx = start_x + (i * res)
                start = (sx, sy)
                ey = (dps * dps_scale) + start_y
                ex = start_x + ((i+1) * res)
                end = (ex, ey)
                lines.add((start, end))
                last_dps = dps
            
        
            draw_world_lines(screen, lines, world_size, window_size, heroes[h]['color'])


def main():
    window_width = 1920
    window_height = 1080
    window_size = (window_width, window_height)
    border_size = 0.0
    h_border = int(border_size * window_height)
    w_border = h_border
    world_size = (60000, 60000)



    pg.init()

    screen=pg.display.set_mode(window_size,0,32)
    slider = Slider(screen, 100, 100, 800, 40, min=0, max=99, step=1)

    WHITE=(255,255,255)
    BLACK=(0,0,0)
    BLUE=(0,0,255)
    GREY=(100,100,100)

    heroes, items, item_bonuses, level_bonuses = load_dl_data()


    for h in heroes:
        hero = Hero(heroes[h], level_bonuses)
        hero.souls = 47000
        dps_per_soul = hero.get_dps()
        heroes[h]['dps_per_soul'] = dps_per_soul


    icon_size = 60
    add_hero_mm_images(heroes, icon_size)


    running = True
    redraw = True
    slider_p_v = 0
    while running:

        events = pg.event.get() 
        pygame_widgets.update(events)

        if redraw:
            screen.fill(WHITE)
            draw_hero_portraits(heroes, screen, icon_size)
            draw_hero_lines(screen, heroes, world_size, window_size)
            slider.draw()
            redraw = False

        if slider_p_v != slider.getValue():
            slider_p_v = slider.getValue()
            redraw = True


        keys = pg.key.get_pressed()
        for event in events:
            if event.type==QUIT:
                running = False

            if event.type == pg.MOUSEBUTTONUP and event.button == 1:
                for i, h in enumerate(heroes):
                    pos = pg.mouse.get_pos()
                    hi = heroes[h]['icon_rect']
                    if hi.collidepoint(pos):
                        heroes[h]['enabled'] = not heroes[h]['enabled']
                        redraw = True
                        print(h)
                        print(heroes[h]['color'])
                        break
        

        if keys[K_LCTRL] and keys[K_w]:
            running = False

        pg.display.update()
    

    pg.display.quit()
    pg.quit()
    sys.exit()

main()