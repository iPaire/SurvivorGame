from settings import *
from math import atan2, degrees
from random import random,choice
import os

class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos,surf,groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
        self.ground = True


class CollisionSprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf,groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)

class gun(pygame.sprite.Sprite):
    def __init__(self, Player, groups):
        # player conection
        self.player = Player
        self.distance = 80
        self.player_direction = pygame.Vector2(1,0)

        # Sprite setup
        super().__init__(groups)
        self.gun_surf = pygame.image.load(join('images','gun','gun.png')).convert_alpha()
        self.image = self.gun_surf
        self.rect = self.image.get_rect(center = self.player.rect.center + self.player_direction * self.distance)

    
    def get_direction(self):
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        player_pos = pygame.Vector2(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
        if (mouse_pos - player_pos):self.player_direction = (mouse_pos - player_pos).normalize()
        return self.player_direction

    def rotate_gun(self):
        angle = degrees(atan2(self.player_direction.x, self.player_direction.y)) - 90
        if self.player_direction.x > 0:
            self.image = pygame.transform.rotozoom(self.gun_surf, angle, 1)
        else:
            self.image = pygame.transform.rotozoom(self.gun_surf, abs(angle), 1)
            self.image = pygame.transform.flip(self.image,False,True)


    def update(self, _):
        self.get_direction()
        self.rotate_gun()
        self.rect.center = self.player.rect.center + self.player_direction * self.distance

class Bullet(pygame.sprite.Sprite):

    def __init__(self, surf, pos, direction, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(center = pos)
        self.spawn_time = pygame.time.get_ticks()
        self.life_time = 1000
        
        self.direction = direction
        self.speed = 1200

    def update(self,dt):
        self.rect.center += self.direction *self.speed * dt
        if (pygame.time.get_ticks() - self.spawn_time >= self.life_time):
            self.kill()

class Enemy(pygame.sprite.Sprite):

    def __init__(self,pos,frames,groups,player,collision_sprites):
        super().__init__(groups)
        self.player = player

        # imagine
        self.frames,self.frame_index = frames, 0
        self.image = self.frames[self.frame_index]
        self.animation_speed = 6

        #rect / hitbox
        self.rect = self.image.get_rect(center = pos)
        self.hitbox_rect = self.rect.inflate(-65, -80)
        self.collision_sprites = collision_sprites
        self.direction = pygame.Vector2()

        # Stats
        self.speed= 350
        self.health = 100
        self.damage = 35
        self.score_increase = 10

        # Timer
        self.death_time = 0
        self.death_duration = 400

        # Flags
        self.alive = True

    def animate(self,dt):
        self.frame_index += self.animation_speed * dt
        self.image = self.frames[int(self.frame_index)% len(self.frames)]
    
    def move(self,dt):
        # get direction
        player_pos = pygame.Vector2(self.player.rect.center)
        enemy_pos = pygame.Vector2(self.rect.center)
        if (player_pos - enemy_pos) != pygame.Vector2():
            self.direction = (player_pos - enemy_pos).normalize()

        # update rect position
        self.hitbox_rect.centerx += self.direction.x * self.speed * dt
        self.collision('horizontal')
        self.hitbox_rect.centery += self.direction.y * self.speed * dt
        self.collision('vertical')
        self.rect.center = self.hitbox_rect.center

    def collision(self, direction):
        # Verifică toate sprite-urile cu care se intersectează hitbox-ul
        colliders = []
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox_rect):
                colliders.append(sprite)
        
        if not colliders:
            return
        
        # Gestionare coliziuni orizontale
        if direction == 'horizontal':
            if self.direction.x > 0:  # Mișcare spre dreapta
                # Găsește cel mai din stânga sprite
                closest_sprite = min(colliders, key=lambda s: s.rect.left)
                self.hitbox_rect.right = closest_sprite.rect.left
            elif self.direction.x < 0:  # Mișcare spre stânga
                # Găsește cel mai din dreapta sprite
                closest_sprite = max(colliders, key=lambda s: s.rect.right)
                self.hitbox_rect.left = closest_sprite.rect.right
        
        # Gestionare coliziuni verticale
        elif direction == 'vertical':
            if self.direction.y > 0:  # Mișcare în jos
                # Găsește cel mai de sus sprite
                closest_sprite = min(colliders, key=lambda s: s.rect.top)
                self.hitbox_rect.bottom = closest_sprite.rect.top
            elif self.direction.y < 0:  # Mișcare în sus
                # Găsește cel mai de jos sprite
                closest_sprite = max(colliders, key=lambda s: s.rect.bottom)
                self.hitbox_rect.top = closest_sprite.rect.bottom

    def destroy(self):
        self.alive = False
        self.death_time = pygame.time.get_ticks()
        surf = pygame.mask.from_surface(self.frames[0]).to_surface()
        surf.set_colorkey('black')
        self.image = surf

    def death_timer(self):
        if pygame.time.get_ticks() - self.death_time >= self.death_duration:
            self.kill()
    
    def update(self,dt):
        if self.death_time == 0:
            self.move(dt)
            self.animate(dt)
        else:
            self.death_timer()

class CyclopsBoss(pygame.sprite.Sprite):
    def __init__(self, pos, player, groups):
        super().__init__(groups)
        self.player = player
        self.load_animations()
        
        # Stare inițială
        self.state = 'idle'
        self.facing = 'right'
        self.image = self.animations[self.state][self.facing][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox_rect = self.rect.inflate(-90, -90)
        self.health = 1000

        # Stats
        self.speed = 120
        self.max_health = 1000
        self.attack_cooldown = 1500  # ms
        self.score_increase = 50
        self.alive = True



        self.last_attack = pygame.time.get_ticks()

        # Raze
        self.melee_range = 80
        self.ranged_range = 250

        # Animații
        self.anim_index = 0
        self.anim_timer = 0
        self.anim_speed = 0.15

    def load_animations(self):
        self.animations = {
            state: {'left': [], 'right': []}
            for state in ['idle', 'run', 'attack_melee', 'throw_rock', 'laser', 'death']
        }
        desired_width = 300  # lățimea dorită
        desired_height = 300  # înălțimea dorită

        for state in self.animations:
            for dir in ['left', 'right']:
                path = f'images/enemies/ciclop/{state}/{dir}/'
                if not os.path.exists(path): continue
                for file in sorted(os.listdir(path)):
                    img = pygame.image.load(os.path.join(path, file)).convert_alpha()
                    
                    # Redimensionează imaginea
                    img = pygame.transform.scale(img, (desired_width, desired_height))
                    
                    self.animations[state][dir].append(img)


    def update(self, dt):
        if not self.alive:
            self.animate()  # animăm până termină moartea
            return

        if self.health > 0:
            self.move_towards_player(dt)
            self.handle_ai()


        self.animate()


    def move_towards_player(self, dt):
        player_pos = pygame.Vector2(self.player.rect.center)
        my_pos = pygame.Vector2(self.hitbox_rect.center)
        direction = player_pos - my_pos
        distance = direction.length()

        if distance > self.melee_range:
            self.direction = direction.normalize()
            self.hitbox_rect.centerx += self.direction.x * self.speed * dt
            self.hitbox_rect.centery += self.direction.y * self.speed * dt
            self.rect.center = self.hitbox_rect.center
            self.change_state('run')
        else:
            self.change_state('idle')

        # Schimbă direcția vizuală
        self.facing = 'right' if direction.x > 0 else 'left'
        self.distance = distance

    def handle_ai(self):
        now = pygame.time.get_ticks()
        if now - self.last_attack >= self.attack_cooldown:
            if self.distance <= self.melee_range:
                self.change_state('attack_melee')
                self.last_attack = now
            elif self.distance <= self.ranged_range:
                self.change_state(choice(['throw_rock', 'laser']))
                self.last_attack = now

    def change_state(self, new_state):
        if self.state != new_state:
            self.state = new_state
            self.anim_index = 0
            self.anim_timer = 0

    def animate(self):
        frames = self.animations[self.state][self.facing]
        if not frames:
            return

        self.anim_timer += self.anim_speed
        if self.anim_timer >= 1:
            self.anim_timer = 0
            self.anim_index += 1

            if self.anim_index >= len(frames):
                if self.state in ['attack_melee', 'throw_rock', 'laser']:
                    self.change_state('idle')
                elif self.state == 'death':
                    self.anim_index = len(frames) - 1
                else:
                    self.anim_index = 0
        if self.state == 'death' and self.anim_index >= len(frames) - 1:
            self.kill()

        self.image = frames[self.anim_index % len(frames)]
    
    def draw_health_bar(self, surface, offset):
        if not self.alive:
            return

        # Setări dimensiuni
        bar_height = 10
        bar_width = self.hitbox_rect.width * 1.5
        offset_y = -50 

        # Calculează poziția pe ecran ținând cont de camera
        screen_x = self.hitbox_rect.centerx - bar_width//2 + offset.x
        screen_y = self.hitbox_rect.top - offset_y + offset.y

        # Desenare componentelor
        health_ratio = max(0, min(self.health/self.max_health, 1))
        current_width = int(bar_width * health_ratio)
        
        pygame.draw.rect(surface, (255,0,0), (screen_x, screen_y, bar_width, bar_height))
        pygame.draw.rect(surface, (0,255,0), (screen_x, screen_y, current_width, bar_height))
        pygame.draw.rect(surface, (0,0,0), (screen_x, screen_y, bar_width, bar_height), 1)





    def destroy(self):
        if not self.alive:
            return  # Evităm apelul de două ori

        self.alive = False
        self.change_state('death')
        self.anim_index = 0
        self.anim_timer = 0
        self.death_time = pygame.time.get_ticks()
