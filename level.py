import pygame
import csv
from settings import *
from support import *
from tile import *
class Level:
    def __init__(self, level_data, surface):
        self.display_surface = surface
        terrain_layout = import_csv_layout(level_data['terrain'])
        self.terrain_sprites = self.create_tile_group(terrain_layout, 'terrain')
        self.world_shift = -3
    
        grass_layout = import_csv_layout(level_data['grass'])
        self.grass_sprites = self.create_tile_group(grass_layout, 'grass')
        
        crates_layout = import_csv_layout(level_data['crates'])
        self.crates_sprites = self.create_tile_group(crates_layout, 'crates')
        
    def create_tile_group(self, layout, type):
        sprite_group = pygame.sprite.Group()
        for row_index, row in enumerate(layout):
            for col_index , val in enumerate(row):
                if val != '-1' :
                    x = col_index * tile_size
                    y = row_index * tile_size

                    if type == 'terrain':
                        terrain_tile_list = import_cut_graphics('graphics/terrain/terrain_tiles.png')
                        tile_surface = terrain_tile_list[int(val)]                       
                        sprite = StaticTile(tile_size, x, y, tile_surface)
                    if type == 'grass':
                        grass_tile_list = import_cut_graphics("graphics/decoration/grass/grass.png")
                        tile_surface = grass_tile_list[int(val)]
                        sprite = StaticTile(tile_size, x, y, tile_surface)
                    if type == 'crates':
                        sprite = Crate()
                        
                    sprite_group.add(sprite)    
        
        return sprite_group            
        
    def run(self):
        self.terrain_sprites.draw(self.display_surface)
        self.terrain_sprites.update(self.world_shift)
        
        self.grass_sprites.draw(self.display_surface)
        self.grass_sprites.update(self.world_shift)
        
        