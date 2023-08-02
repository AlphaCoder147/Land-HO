import pygame
import csv
from settings import *
from support import *
from tile import *
from enemy import *
from decoration import *
from player import *
from particles import *
class Level:
    def __init__(self, level_data, surface):
        self.display_surface = surface
        terrain_layout = import_csv_layout(level_data['terrain'])
        self.terrain_sprites = self.create_tile_group(terrain_layout, 'terrain')
        self.world_shift = 0
        self.dust_sprite = pygame.sprite.GroupSingle()
        self.player_on_ground = False
        self.current_x = None
    
        player_layout = import_csv_layout(level_data['player'])
        self.player = pygame.sprite.GroupSingle()
        self.goal = pygame.sprite.GroupSingle()
        self.player_setup(player_layout)
        
        grass_layout = import_csv_layout(level_data['grass'])
        self.grass_sprites = self.create_tile_group(grass_layout, 'grass')
        
        crates_layout = import_csv_layout(level_data['crates'])
        self.crates_sprites = self.create_tile_group(crates_layout, 'crates')
        
        coins_layout = import_csv_layout(level_data['coins'])
        self.coins_sprites = self.create_tile_group(coins_layout, 'coins')
        
        fg_trees_layout = import_csv_layout(level_data['trees_fg'])
        self.fg_trees_sprites = self.create_tile_group(fg_trees_layout, 'fg_trees')
        
        bg_trees_layout = import_csv_layout(level_data['trees_bg'])
        self.bg_trees_sprites = self.create_tile_group(bg_trees_layout, 'bg_trees')
        
        enemy_layout = import_csv_layout(level_data['enemies'])
        self.enemies_sprites = self.create_tile_group(enemy_layout, 'enemies')
        
        constraint_layout = import_csv_layout(level_data['constraints'])
        self.constraint_sprites = self.create_tile_group(constraint_layout, 'constraints')
        
        self.sky = Sky(8)
        level_width = len(terrain_layout[0]) * tile_size
        self.water = Water(screen_height - 40, level_width)
        self.cloud = Clouds(400, level_width,20)
        
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
                        sprite = Crate(tile_size, x, y)
                    if type == 'coins':
                        if val == '0' : sprite = Coin(tile_size, x, y, 'graphics/coins/gold')
                        if val == '1' : sprite = Coin(tile_size, x, y, 'graphics/coins/silver')
                    if type == 'fg_trees':
                        if val == '5' or '2' : sprite = Palm(tile_size, x, y, 'graphics/terrain/palm_small', 38)    
                        if val == '6' or '3' : sprite = Palm(tile_size,x,y,'graphics/terrain/palm_large', 64)
                    if type == 'bg_trees':
                        sprite = Palm(tile_size, x, y, 'graphics/terrain/palm_bg', 64)
                    if type == 'enemies':
                        sprite = Enemy(tile_size, x, y)
                    if type == 'constraints':
                        sprite = Tile(tile_size, x, y)
                        
                    sprite_group.add(sprite)    
        
        return sprite_group            
    
    def enemy_collision_reverse(self):
        for enemy in self.enemies_sprites.sprites():
            if pygame.sprite.spritecollide(enemy, self.constraint_sprites, False):
                enemy.reverse()
    
    def player_setup(self, layout):
        sprite_group = pygame.sprite.Group()
        for row_index, row in enumerate(layout):
            for col_index , val in enumerate(row):
                x = col_index * tile_size
                y = row_index * tile_size
                if val == '0' :
                    sprite = Player((x, y), self.display_surface, self.create_jump_particles)
                    self.player.add(sprite)      
                if val == '1':
                    hat_surface = pygame.image.load('graphics/character/hat.png').convert_alpha()
                    sprite = StaticTile(tile_size, x, y, hat_surface)
                    self.goal.add(sprite)
                    
    def create_jump_particles(self, pos):
        if self.player.sprite.facing_right:
            pos -= pygame.math.Vector2(10,5)
        else:
            pos += pygame.math.Vector2(10, -5)    
        jump_particle_sprite = ParticleEffect(pos, 'jump')
        self.dust_sprite.add(jump_particle_sprite)
    
    def horizontal_movement_collison(self):
        player = self.player.sprite
        player.rect.x += player.direction.x * player.speed
        collidables = self.terrain_sprites.sprites() + self.crates_sprites.sprites() #+ self.fg_trees_sprites.sprites()
        for sprite in collidables:
            if sprite.rect.colliderect(player.rect):
                if player.direction.x < 0:
                    player.rect.left = sprite.rect.right
                    player.on_left = True
                    self.current_x = player.rect.left
                elif player.direction.x > 0:
                    player.rect.right = sprite.rect.left   
                    player.on_right = True 
                    self.current_x = player.rect.right
                    
        if player.on_left and (player.rect.left < self.current_x or player.direction.x >= 0):
            player.on_left = False
        if player.on_right and (player.rect.right > self.current_x or player.direction.x <= 0):
            player.on_right = False    
                        
    def scroll_x(self):
        player = self.player.sprite
        player_x = player.rect.centerx
        direction_x = player.direction.x
        
        if player_x < screen_width / 4 and direction_x < 0:
            self.world_shift = 8
            player.speed = 0    
        elif player_x > screen_width - (screen_width / 4) and direction_x > 0:
            self.world_shift = -8
            player.speed = 0
        else:
            self.world_shift = 0
            player.speed = 7
    
    
    def vertical_movement_collision(self):
        player = self.player.sprite
        player.apply_gravity()
        collidables = self.terrain_sprites.sprites() + self.crates_sprites.sprites() #+ self.fg_trees_sprites.sprites()
        
        for sprite in collidables:
            if sprite.rect.colliderect(player.rect):
                if player.direction.y > 0:
                    player.rect.bottom = sprite.rect.top
                    player.direction.y = 0
                    player.on_ground = True
                    
                elif player.direction.y < 0:
                    player.rect.top = sprite.rect.bottom 
                    player.direction.y = 0
                    player.on_ceiling = True
        
        if player.on_ground and player.direction.y < 0 or player.direction.y > 1:
            player.on_ground = False
        if player.on_ceiling and player.direction.y > 0:
            player.on_ceiling = False
    
    def create_jump_particles(self, pos):
        if self.player.sprite.facing_right:
            pos -= pygame.math.Vector2(10,5)
        else:
            pos += pygame.math.Vector2(10, -5)    
        jump_particle_sprite = ParticleEffect(pos, 'jump')
        self.dust_sprite.add(jump_particle_sprite)
    
    def get_player_on_ground(self):
        if self.player.sprite.on_ground:
            self.player_on_ground = True
        else:
            self.player_on_ground = False    
            
    def create_landing_dust(self):
        if not self.player_on_ground and self.player.sprite.on_ground and not self.dust_sprite.sprite:
            if self.player.sprite.facing_right:
                offset = pygame.math.Vector2(10, 15)
            else:
                offset = pygame.math.Vector2(-10, 15)
                    
            fall_dust_particles = ParticleEffect(self.player.sprite.rect.midbottom - offset, 'land')
            self.dust_sprite.add(fall_dust_particles)
                            
    def run(self):
        self.sky.draw(self.display_surface)

        self.water.draw(self.display_surface, self.world_shift)

        self.cloud.draw(self.display_surface, self.world_shift)

        self.terrain_sprites.draw(self.display_surface)
        self.terrain_sprites.update(self.world_shift)
        
        self.grass_sprites.draw(self.display_surface)
        self.grass_sprites.update(self.world_shift)
        
        self.coins_sprites.update(self.world_shift)
        self.coins_sprites.draw(self.display_surface)
        
        self.bg_trees_sprites.update(self.world_shift)
        self.bg_trees_sprites.draw(self.display_surface)

        self.enemies_sprites.update(self.world_shift)
        self.constraint_sprites.update(self.world_shift)
        self.enemy_collision_reverse()
        self.enemies_sprites.draw(self.display_surface)
        
        self.crates_sprites.update(self.world_shift)
        self.crates_sprites.draw(self.display_surface)
        
        self.fg_trees_sprites.update(self.world_shift)
        self.fg_trees_sprites.draw(self.display_surface)
        
        self.dust_sprite.update(self.world_shift)
        self.dust_sprite.draw(self.display_surface)
        
        self.player.update()
        self.horizontal_movement_collison()
        self.get_player_on_ground()
        self.vertical_movement_collision()
        self.create_landing_dust()
        self.scroll_x()
        self.player.draw(self.display_surface)
        self.goal.update(self.world_shift)
        self.goal.draw(self.display_surface)
        
        