import pygame
import random
from enum import Enum
from pygame import mixer

pygame.init()
pygame.display.set_caption("Tanks") 
screen = pygame.display.set_mode((800,600)) 
mixer.music.load("Music/1.wav") 

hit = mixer.Sound("Music/hit.wav")
GG = mixer.Sound("Music/GG_tank.wav")
shoot = mixer.Sound("Music/shoot.wav")
wall_break = mixer.Sound("Music/wall.wav")
pwrup = mixer.Sound("Music/powerup.wav")


class Direction(Enum): 
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

class shot(Enum): 
    SHOT = 1

class Info_screen:
    def __init__(self):
        self.x = 800
        self.y = 0
        self.width = 300
        self.height = 600
        self.color = (4,104,115)
    
    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

class Tank:
    def __init__(self, color, color1, Place_y, d_right = pygame.K_RIGHT, d_left = pygame.K_LEFT, d_up = pygame.K_UP, d_down = pygame.K_DOWN):
        self.x = random.randint(200,600)
        self.y = random.randint(200,400)
        self.Place_y = Place_y
        self.speed = 3
        self.color = color
        self.color1 = color1
        self.width = 31
        self.life_count = 3
        self.direction = Direction.RIGHT
        self.KEYS = {d_right: Direction.RIGHT, d_left: Direction.LEFT,
                     d_up: Direction.UP, d_down: Direction.DOWN}
        
    def draw(self):
        Centre_tank = (self.x + self.width // 2, self.y + self.width // 2)

        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.width),6)
        pygame.draw.circle(screen, self.color1, Centre_tank, self.width // 2,4)
        
        if self.direction == Direction.RIGHT:
            pygame.draw.line(screen, self.color1, 
                             (Centre_tank[0] + 19, Centre_tank[1]), (self.x + self.width + self.width // 2, self.y + self.width // 2), 2)
        if self.direction == Direction.LEFT:
            pygame.draw.line(screen, self.color1, 
                             (Centre_tank[0] - 19, Centre_tank[1]), (self.x - self.width // 2, self.y + self.width // 2), 2)
        if self.direction == Direction.UP:
            pygame.draw.line(screen, self.color1, 
                             (Centre_tank[0], Centre_tank[1] - 20), (self.x + self.width // 2, self.y - self.width // 2), 2)
        if self.direction == Direction.DOWN:
            pygame.draw.line(screen, self.color1, 
                             (Centre_tank[0], Centre_tank[1] + 19), (self.x + self.width // 2, self.y + self.width + self.width // 2), 2)

    def Change_dir(self, direction):
        self.direction = direction

    def random_pos(self):
        self.x = random.randint(200,600)
        self.y = random.randint(200,400)

    def life_counter(self):
        font = pygame.font.Font('freesansbold.ttf', 36)
        text = font.render("Lives: " + str(self.life_count), 1, self.color)
        place = text.get_rect(center=(950, self.Place_y))
        screen.blit(text, place)

    def move(self):
        if self.direction == Direction.RIGHT:  
            self.x += self.speed               
        if self.direction == Direction.LEFT:
            self.x -= self.speed
        if self.direction == Direction.UP:
            self.y -= self.speed
        if self.direction == Direction.DOWN:
            self.y += self.speed
        if self.x > 800:     
            self.x = -40          
        if self.x < -40:           
            self.x = 800
        if self.y > 600:
            self.y = -40
        if self.y < -40:
            self.y = 600

        self.draw()

class Bullet:
    def __init__(self, tank, shoot = pygame.K_RETURN):
        self.bullet_x = -100
        self.bullet_y = -100
        self.bullet_speed = 15
        self.tank = tank
        self.bullet_width = 15
        self.bullet_height = 3
        self.is_fired = False
        self.direction = Direction.RIGHT
        self.KEYS = {shoot: shot.SHOT}

    def bullet_pos(self):
        if self.direction == Direction.RIGHT and self.is_fired == False:
            self.bullet_x = self.tank.x + self.tank.width + self.tank.width // 2
            self.bullet_y = self.tank.y + self.tank.width // 2
            self.bullet_width = 15
            self.bullet_height = 3
        if self.direction == Direction.LEFT and self.is_fired == False:
            self.bullet_x = self.tank.x - self.tank.width // 2
            self.bullet_y = self.tank.y + self.tank.width // 2
            self.bullet_width = 15
            self.bullet_height = 3
        if self.direction == Direction.UP and self.is_fired == False:
            self.bullet_x = self.tank.x + self.tank.width // 2
            self.bullet_y = self.tank.y - self.tank.width // 2
            self.bullet_width = 3
            self.bullet_height = 15
        if self.direction == Direction.DOWN and self.is_fired == False:
            self.bullet_x = self.tank.x + self.tank.width // 2
            self.bullet_y = self.tank.y + self.tank.width + self.tank.width // 2
            self.bullet_width = 3
            self.bullet_height = 15       

    def draw_bullet(self):
        if self.is_fired:
            if self.direction == Direction.RIGHT:
                pygame.draw.rect(screen, self.tank.color, (self.bullet_x, self.bullet_y, self.bullet_width, self.bullet_height))
            if self.direction == Direction.LEFT:
                pygame.draw.rect(screen, self.tank.color, (self.bullet_x - self.bullet_width, self.bullet_y, self.bullet_width, self.bullet_height))
            if self.direction == Direction.UP:
                pygame.draw.rect(screen, self.tank.color, (self.bullet_x, self.bullet_y - self.bullet_height, self.bullet_width, self.bullet_height))
            if self.direction == Direction.DOWN:
                pygame.draw.rect(screen, self.tank.color, (self.bullet_x, self.bullet_y, self.bullet_width, self.bullet_height))      

    def fire_false(self):
        if self.bullet_x >= 800:
            self.is_fired = False
        if self.bullet_x <= 0:
            self.is_fired = False
        if self.bullet_y >= 600:
            self.is_fired = False
        if self.bullet_y <= 0:
            self.is_fired = False

    def direction_bullet(self):
        if self.is_fired == False:
            self.direction = self.tank.direction

    def move_bullet(self):
        if self.direction == Direction.RIGHT:
            self.bullet_x += self.bullet_speed
        if self.direction == Direction.LEFT:
            self.bullet_x -= self.bullet_speed
        if self.direction == Direction.UP:
            self.bullet_y -= self.bullet_speed
        if self.direction == Direction.DOWN:
            self.bullet_y += self.bullet_speed

        self.draw_bullet()
        self.direction_bullet()
        self.fire_false()

    def collision_tank(self,tank_enemy):
        lx1 = self.bullet_x
        lx2 = tank_enemy.x
        rx1 = self.bullet_x + self.bullet_width
        rx2 = tank_enemy.x + tank_enemy.width
        ty1 = self.bullet_y
        ty2 = tank_enemy.y
        by1 = self.bullet_y + self.bullet_height
        by2 = tank_enemy.y + tank_enemy.width
        lx = max(lx1, lx2)
        rx = min(rx1, rx2)
        ty = max(ty1, ty2)
        by = min(by1, by2)
        if lx <= rx and ty <= by:
            return True
        return False

class Wall:
    def __init__(self):
        self.x = random.randint(50,750)
        self.y = random.randint(50,550)
        self.width = 20
        self.height = 70

        rand = random.randint(1,4)
        if rand == 1:
            self.direction = Direction.RIGHT
        if rand == 2:
            self.direction = Direction.LEFT
        if rand == 3:
            self.direction = Direction.UP
        if rand == 4:
            self.direction = Direction.DOWN
   
    def draw(self):
        if self.direction == Direction.RIGHT or self.direction == Direction.LEFT:
            self.width = 20
            self.height = 70
        if self.direction == Direction.UP or self.direction == Direction.DOWN:
            self.width = 70
            self.height = 20
        pygame.draw.rect(screen,(219,65,22),(self.x,self.y,self.width,self.height))
    
    def collision_bullet(self, bullet):
        lx1 = self.x
        lx2 = bullet.bullet_x
        rx1 = self.x + self.width
        rx2 = bullet.bullet_x + bullet.bullet_width
        ty1 = self.y
        ty2 = bullet.bullet_y
        by1 = self.y + self.height
        by2 = bullet.bullet_y + bullet.bullet_width
        lx = max(lx1, lx2)
        rx = min(rx1, rx2)
        ty = max(ty1, ty2)
        by = min(by1, by2)
        if lx <= rx and ty <= by:
            return True
        return False

    def collision_tank(self, tank):
        lx1 = self.x
        lx2 = tank.x
        rx1 = self.x + self.width
        rx2 = tank.x + tank.width
        ty1 = self.y
        ty2 = tank.y
        by1 = self.y + self.height
        by2 = tank.y + tank.width
        lx = max(lx1, lx2)
        rx = min(rx1, rx2)
        ty = max(ty1, ty2)
        by = min(by1, by2)
        if lx <= rx and ty <= by:
            return True
        return False

class Yabloko:
    def __init__(self):
        self.x = 400
        self.y = 500
        self.radius = 20
    
    def draw(self):
        pygame.draw.circle(screen, (14,196,199), (self.x,self.y), self.radius)
        pygame.draw.line(screen,(255,255,255),(399,490),(399,510), 2)
        pygame.draw.line(screen,(255,255,255),(399,490),(392,500), 2)
        pygame.draw.line(screen,(255,255,255),(399,490),(406,500), 2)
        
    def collision_tank(self, tank):
        lx1 = self.x - self.radius
        lx2 = tank.x
        rx1 = self.x + self.radius
        rx2 = tank.x + tank.width
        ty1 = self.y - self.radius
        ty2 = tank.y
        by1 = self.y + self.radius 
        by2 = tank.y + tank.width
        lx = max(lx1, lx2)
        rx = min(rx1, rx2)
        ty = max(ty1, ty2)
        by = min(by1, by2)
        if lx <= rx and ty <= by:
            return True
        return False
        
def igra():
    mixer.music.play(-1)
    game = True

    music_gg = False
    tt = 0

    tank0 = Tank((35,187,17), (35,107,17), 50)
    tank1 = Tank((255,170,35), (255,120,35), 100, pygame.K_d, pygame.K_a, pygame.K_w, pygame.K_s)
    tanks = [tank0, tank1]

    bullet0 = Bullet(tank0)
    bullet1 = Bullet(tank1, pygame.K_SPACE)
    bullets  = [bullet0, bullet1]
    wall0 = Wall()
    wall1 = Wall()
    wall2 = Wall()
    wall3 = Wall()
    wall4 = Wall()
    wall5 = Wall()
    walls = [wall0,wall1,wall2,wall3,wall4,wall5]
    
    apple0 = Yabloko()
    apples = [apple0]

    infa = Info_screen()
    
    FPS = 60
    clock = pygame.time.Clock()
    
    secs0 = 0
    secs1 = 0
    rand = random.randint(7,11)
    plus_one0 = False
    plus_one1 = False
    #vum0 = False
    #vum1 = False
    pwr = False

    while game:
        mills = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game = False 

            if event.type == pygame.KEYDOWN:
                for tank in tanks:
                    if event.key in tank.KEYS.keys():
                        tank.Change_dir(tank.KEYS[event.key])
                for bullet in bullets:
                    if event.key in bullet.KEYS.keys():
                        bullet.direction_bullet()
                        bullet.bullet_pos()
                        if bullet.is_fired == False:
                            shoot.play()
                        bullet.is_fired = True

        screen.fill((0,0,0))
        for apple in apples:
            apple.draw()

            if apple.collision_tank(tank0):
                apples.remove(apple)
                plus_one0 = True
                #vum0 = True
                pwr = True

            if apple.collision_tank(tank1):
                apples.remove(apple)
                plus_one1 = True
                #vum1 = True
                pwr = True
        
        if plus_one0:
            secs0 = secs0 + (mills / 1000)
        if plus_one1:
            secs1 = secs1 + (mills / 1000)

        if secs0 < 5 and secs0 != 0  and tank1.life_count > 0 and tank0.life_count > 0:
            tank0.speed = 6
            bullet0.bullet_speed = 30
            l0 = 5 - secs0
            ll0 = "%.2f" % l0
            font = pygame.font.Font('freesansbold.ttf', 20)     
            text = font.render(ll0, 1, (35,187,17)) 
            place = text.get_rect(center = (400,100))   
            screen.blit(text, place)
            if pwr:
                pwrup.play()
                pwr = False

        elif secs0 >= 5 and tank0.life_count > 0 and tank1.life_count > 0:
            tank0.speed = 3
            bullet0.bullet_speed = 15
            
        if secs1 < 5 and secs1 != 0  and tank0.life_count > 0 and tank1.life_count > 0:
            tank1.speed = 6
            bullet1.bullet_speed = 30

            l1 = 5 - secs1
            ll1 = "%.2f" % l1

            font = pygame.font.Font('freesansbold.ttf', 20)     
            text = font.render(ll1, 1, (255,170,35)) 
            place = text.get_rect(center = (400,100))   
            screen.blit(text, place) 
            if pwr:
                pwrup.play()
                pwr = False

        elif secs1 >= 5 and tank1.life_count > 0 and tank0.life_count > 0:
            tank1.speed = 3
            bullet1.bullet_speed = 15

        

        if secs0 >= rand:
            secs0 = 0
            #vum0 = False
            apples.append(Yabloko())
            plus_one0 = False
            rand = random.randint(7,11)
        if secs1 >= rand:
            #vum1 = False
            secs1 = 0
            apples.append(Yabloko())
            plus_one1 = False
            rand = random.randint(7,11)

        for wall in walls:
            wall.draw()
            if wall.collision_bullet(bullet0):
                walls.remove(wall)
                bullet0.bullet_x = -100
                bullet0.bullet_y = -100
                bullet0.is_fired = False
                wall_break.play()
            if wall.collision_bullet(bullet1):
                walls.remove(wall)
                bullet1.bullet_x = -100
                bullet1.bullet_y = -100
                bullet1.is_fired = False
                wall_break.play()
            if wall.collision_tank(tank0):
                walls.remove(wall)
                tank0.random_pos()
                tank0.life_count -= 1
                wall_break.play()
            if wall.collision_tank(tank1):
                walls.remove(wall)
                tank1.random_pos()
                tank1.life_count -= 1
                wall_break.play()

        for tank in tanks:
            tank.move()
            if tank.life_count <= 0:
                tank0.speed = 0                 
                tank1.speed = 0
                bullet0.bullet_speed = 0
                bullet1.bullet_speed = 0
                bullet0.is_fired = True         
                bullet1.is_fired = True
                bullet0.bullet_x = 1100         
                bullet1.bullet_x = 1100
                mixer.music.pause()              
                music_gg = True
                tank0.x = 55
                tank0.y = 120
                tank0.direction = Direction.UP
                tank1.x = 695
                tank1.y = 120 
                tank1.direction = Direction.UP
                font = pygame.font.Font('freesansbold.ttf', 80)     
                text = font.render("Game Over", 1, (237,20,0)) 
                place = text.get_rect(center = (400,275))   
                screen.blit(text, place)                    

                font1 = pygame.font.Font('freesansbold.ttf', 30)
                text1 = font1.render("Press [ESC] to Exit", 1, (0,22,255))
                place1 = text1.get_rect(center = (400, 335))
                screen.blit(text1, place1)

                font2 = pygame.font.Font('freesansbold.ttf', 30)
                text2 = font2.render("Press [R] to Restart", 1, (0,22,255))
                place2 = text2.get_rect(center = (400, 375))
                screen.blit(text2, place2)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                    if event.key == pygame.K_r:
                        game = False
                        igra()

        if music_gg == True and tt == 0:
            GG.play()
            tt = 1

        for bullet in bullets:    
            bullet.move_bullet()
        if bullet0.collision_tank(tank1):
            if music_gg == False:
                hit.play()
            tank1.random_pos()
            tank1.life_count -= 1
            bullet0.bullet_x = -100
            bullet0.bullet_y = -100
            bullet0.is_fired = False

        if bullet1.collision_tank(tank0):
            if music_gg == False:
                hit.play()
            tank0.random_pos()
            tank0.life_count -= 1
            bullet1.bullet_x = -100
            bullet1.bullet_y = -100
            bullet1.is_fired = False

        infa.draw()

        for tank in tanks:
            tank.life_counter()
        pygame.display.flip()