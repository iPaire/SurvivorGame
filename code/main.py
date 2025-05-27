from settings import *
from player import Player
from sprites import *
from pytmx.util_pygame import load_pygame
from groups import AllSprites
from functions import *

from random import randint,choice

class Game:
    def __init__(self):
        # setup
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT))
        pygame.display.set_caption('joc scheleti')
        self.clock = pygame.time.Clock()
        self.running = True

        #Variabile Functionale / flags
        self.fullscreen = False 
        self.paused = False
        self.paused_last_frame = False  

        # Timer pentru fullscreen
        self.last_fullscreen_time = 0
        self.fullscreen_cooldown = 300  # 300 ms cooldown
        
        # Font
        self.font = pygame.font.SysFont("Arial", 30)


        # Grupe
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group() 
        self.enemy_sprites = pygame.sprite.Group() 
        self.boss_sprites = pygame.sprite.Group()

        # Progresie
        self.score = 300
        self.level = 0
        self.boss_spawned = False

        self.spawn_pos_bossx = 0
        self.spawn_pos_bossy = 0
         # arma
        self.can_shoot = True
        self.shoot_time = 0
        self.gun_cooldown = 600
        self.bullet_distance = 50
        self.bullet_damage = 100
        # inamici
        self.enemy_event = pygame.event.custom_type()
        self.Spawn_Interval = 1000
        pygame.time.set_timer(self.enemy_event, self.Spawn_Interval) # timer spawn inamici
        self.spawn_positions = []
        
        # Audio
        self.shoot_sound = pygame.mixer.Sound(join('audio','shoot.wav'))
        self.shoot_sound.set_volume(0.2)
        self.impact_sound = pygame.mixer.Sound(join('audio','impact.ogg'))
        self.impact_sound.set_volume(0.2)
        self.bg_music = pygame.mixer.Sound(join('audio', 'music.wav'))
        self.bg_music.set_volume(0.1)
        self.bg_music.play(loops=-1)

        #setup
        self.load_images()
        self.setup()

    def load_images(self):
        """ pentru imagini simple"""
        self.bullet_surf = pygame.image.load(join('images','gun','bullet.png')).convert_alpha()  # glont

        folders = list(walk(join('images','enemies')))[0][1]
        self.enemy_frames = {}
        for folder in folders:
            if folder == 'ciclop':
                continue
            for folder_path, _,  file_names in walk(join('images','enemies',folder)):
                self.enemy_frames[folder] = []
                for file_name in sorted(file_names, key = lambda name: int(name.split('.')[0])):
                    full_path = join(folder_path,file_name)
                    surf= pygame.image.load(full_path).convert_alpha()
                    self.enemy_frames[folder].append(surf)

    def load_animation(folder_path):
        """ pentru boss deocamdata"""
        frames = []
        for filename in sorted(os.listdir(folder_path)):
            if filename.endswith(".png"):
                img_path = os.path.join(folder_path, filename)
                image = pygame.image.load(img_path).convert_alpha()
                frames.append(image)
        return frames

    def input(self):
        keys = pygame.key.get_pressed()
        current_time = pygame.time.get_ticks()
        if pygame.mouse.get_pressed()[0] and self.can_shoot:
            self.shoot_sound.play()
            pos = self.gun.rect.center + self.gun.player_direction * self.bullet_distance
            Bullet(self.bullet_surf, pos,self.gun.player_direction,(self.all_sprites, self.bullet_sprites))
            self.can_shoot = False
            self.shoot_time = current_time
        if pygame.key.get_pressed()[pygame.K_f] and current_time - self.last_fullscreen_time > self.fullscreen_cooldown:
            self.fullscreen, self.display_surface = toggle_fullscreen(self.fullscreen, self.display_surface)
            self.last_fullscreen_time = current_time  
        if keys[pygame.K_p] and not self.paused_last_frame:
            self.paused = toggle_pause(self.paused)
            self.paused_last_frame = True  # Ținem minte că pauza a fost apăsată
        elif not keys[pygame.K_p]:
            self.paused_last_frame = False  # Resetează când tasta nu mai este apăsată




    def increase_score(self, points):
        """Adaugă puncte la scorul jucătorului.
            si urca nivelele si are tot algoritmul de progresie
        """
        self.score += points
        if not self.boss_sprites:
            boss_spawned = False
        if self.score >= 500 and self.level == 0 and not self.boss_spawned:    # La 500 de score creste dificultatea sau intra un boss inca ma gandesc ce fac
            self.level += 1 
            self.Spawn_Interval = 500
            self.spawn_Cyclop()
            
            boss_spawned = True
            print(f"Ai ajuns la levelul {self.level} acum intervalul de spawn este: {self.Spawn_Interval} ms")

        if self.score >= 1000 and self.level == 1 and not self.boss_spawned:    # La 500 de score creste dificultatea sau intra un boss inca ma gandesc ce fac
            self.level += 1
            self.Spawn_Interval = 500
            self.spawn_Cyclop()
            self.spawn_Cyclop()
            boss_spawned = True
    def spawn_Cyclop(self, quantity = 1):
        x_offset = randint(-50, 50)
        y_offset = randint(-50, 50)
        
        cyclops = CyclopsBoss(
            (self.spawn_pos_bossx + x_offset, self.spawn_pos_bossy + y_offset),
            player=self.player,
            groups=[self.all_sprites, self.enemy_sprites, self.boss_sprites]
        )

    def draw_score(self, display_surface):
        """Desenează scorul pe ecran."""
        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        display_surface.blit(score_text, (10, 10))  # Poziția scorului pe ecran

    def gun_timer(self):
        """ Activeaza un timeaza un timer pentru urmatorul timp in care playerul poate trage"""
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.shoot_time >= self.gun_cooldown:
                self.can_shoot = True
    
    def game_over(self):
        """Afișează mesajul de 'Game Over'."""
        self.bg_music.stop()
        game_over_text = self.font.render("Game Over", True, (255, 0, 0))
        self.display_surface.blit(game_over_text, (WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 - 50))
        pygame.display.update()
        pygame.time.wait(3000) 
        pygame.quit()
        exit()

    def draw_health(self, display_surface):
        """Desenează viața jucătorului pe ecran."""
        health_text = self.font.render(f"Health: {self.player.health}", True, (255, 0, 0))
        display_surface.blit(health_text, (10, 40))  # Poziția vieții pe ecran

    def draw_health_bar(self, display_surface):
        """Desenează o bară vizuală de viață."""
        bar_width = 200
        bar_height = 20
        current_health = (self.player.health / 100) * bar_width
        pygame.draw.rect(display_surface, (255, 0, 0), (10, 70, bar_width, bar_height))  # Bara completă
        pygame.draw.rect(display_surface, (0, 255, 0), (10, 70, current_health, bar_height))  # Bara cu viața

    def decrease_health(self, amount):
        """Scade viața jucătorului."""
        effective_damage = max(amount - self.player.defense, 1)
        self.player.health -= effective_damage
        if self.player.health <= 0:
            self.game_over()


    def check_collision(self):
        if self.bullet_sprites:
            for bullet in self.bullet_sprites:
                Collision_sprites = pygame.sprite.spritecollide(bullet, self.enemy_sprites, False, pygame.sprite.collide_mask)
                if Collision_sprites:
                    self.impact_sound.play()
                    for sprite in Collision_sprites:
                        if sprite.alive :
                            sprite.health -= self.bullet_damage
                            if sprite.health <= 0 :
                                self.increase_score(sprite.score_increase)
                                sprite.destroy()
                    bullet.kill()

        enemy_coliding = pygame.sprite.spritecollide(self.player, self.enemy_sprites, False,pygame.sprite.collide_mask)
        if (enemy_coliding):
            for sprite in enemy_coliding:
                if sprite not in self.boss_sprites:
                    if self.player.health>0:
                        self.decrease_health(sprite.damage)
                    sprite.kill()
    
            

    def setup(self):
         map = load_pygame(join('data','maps','mapa.tmx'))

         for x,y,image in map.get_layer_by_name('Ground').tiles():
            Sprite((x * TILE_SIZE,y * TILE_SIZE), image, self.all_sprites)
        
         for obj in map.get_layer_by_name('Objects'):
            CollisionSprite((obj.x,obj.y),obj.image,(self.all_sprites,self.collision_sprites))
         for obj in map.get_layer_by_name('Collisions'):
            CollisionSprite((obj.x, obj.y),pygame.Surface((obj.width, obj.height)),self.collision_sprites)

         for obj in map.get_layer_by_name('Entities'):
             if obj.name == 'Player':
                self.player = Player((obj.x, obj.y),self.all_sprites, self.collision_sprites)
                self.spawn_pos_bossx,self.spawn_pos_bossy = obj.x, obj.y
                self.gun = gun(self.player,self.all_sprites)
             elif obj.name == 'Enemy':
                 self.spawn_positions.append((obj.x,obj.y))



    def run(self):
        pygame.mouse.set_visible(True)  # STERGE DUPA DEBUGGING
        while self.running:
            #delta timp
            dt = self.clock.tick() / 1000
            # loop de event
            for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    if event.type == self.enemy_event:
                        Enemy(choice(self.spawn_positions), choice(list(self.enemy_frames.values())) , (self.all_sprites,self.enemy_sprites),self.player, self.collision_sprites)


            self.input()
            # Update
            if not self.paused:
                self.gun_timer()
                self.all_sprites.update(dt)
                self.check_collision()

            current_offset = self.all_sprites.offset

            #draw
            if self.paused:
                draw_pause_screen(self.display_surface, WINDOW_WIDTH, WINDOW_HEIGHT)
            else:
                self.display_surface.fill('black')
                self.all_sprites.draw(self.player.rect.center)
            


            self.draw_health(self.display_surface)
            self.draw_health_bar(self.display_surface)
            self.draw_score(self.display_surface)

            for enemy in self.boss_sprites:
                enemy.draw_health_bar(self.display_surface,current_offset)

            pygame.display.update()

        pygame.quit()

if __name__ == '__main__':
    print("Loading Game...")
    game = Game()
    game.run()


""" 
    --- TO DO ---
  inamici sa arunce viata si munitie random
  More Weapons
  Increasing Difficulty
  Roguelike System
  Bosses and progression
  co-op multiplayer


  pentru a adauga arme noi trebuie sa misc statusurile si tot ce tine de arma din game si sa il pun intr-un fisier separat dupa fac mai multe clase de arme si apoi fac obiecte separate de arme si inca ma 
  gandesc cum sa fac sa le adaug

"""
