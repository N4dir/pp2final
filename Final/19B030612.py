import pygame
import pika
import sys
import random
from enum import Enum
import uuid
import json
from threading import Thread
from pygame import mixer


pygame.init()
width = 1100
height = 600
pygame.display.set_caption("Tanks")
screen = pygame.display.set_mode((width,height))


screen_single = pygame.display.set_mode((1100,600)) 


hit = mixer.Sound("Music/hit.wav")
GG = mixer.Sound("Music/GG_tank.wav")
shoot = mixer.Sound("Music/shoot.wav")
wall_break = mixer.Sound("Music/wall.wav")
pwrup = mixer.Sound("Music/powerup.wav")

mixer.music.load('Music_online/bg_online.wav')

hit_self = mixer.Sound('Music_online/hit_self.wav')
shot_enemy = mixer.Sound('Music_online/shot_enemy.wav')
other_hit = mixer.Sound('Music_online/other_hit.wav')
self_dead = mixer.Sound('Music_online/self_dead.wav')
self_win = mixer.Sound('Music_online/self_win.wav')
out_of_time = mixer.Sound('Music_online/out_of_time.wav')
self_shot = mixer.Sound('Music_online/self_shot.wav')
self_kicked = mixer.Sound('Music_online/self_kicked.wav')
self_kicked_ai = mixer.Sound('Music_online/self_kicked.wav')
self_dead_ai = mixer.Sound('Music_online/self_dead.wav')
self_win_ai = mixer.Sound('Music_online/self_win.wav')


ip = '34.254.177.17'
RabbitPort = '5672'
vhost = 'dar-tanks'
credents = pika.PlainCredentials(username = 'dar-tanks', password ='5orPLExUYnyVYZg48caMpX')


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
        pygame.draw.rect(screen_single, self.color, (self.x, self.y, self.width, self.height))

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

        pygame.draw.rect(screen_single, self.color, (self.x, self.y, self.width, self.width),6)
        pygame.draw.circle(screen_single, self.color1, Centre_tank, self.width // 2,4)
        
        if self.direction == Direction.RIGHT:
            pygame.draw.line(screen_single, self.color1, 
                             (Centre_tank[0] + 19, Centre_tank[1]), (self.x + self.width + self.width // 2, self.y + self.width // 2), 2)
        if self.direction == Direction.LEFT:
            pygame.draw.line(screen_single, self.color1, 
                             (Centre_tank[0] - 19, Centre_tank[1]), (self.x - self.width // 2, self.y + self.width // 2), 2)
        if self.direction == Direction.UP:
            pygame.draw.line(screen_single, self.color1, 
                             (Centre_tank[0], Centre_tank[1] - 20), (self.x + self.width // 2, self.y - self.width // 2), 2)
        if self.direction == Direction.DOWN:
            pygame.draw.line(screen_single, self.color1, 
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
        screen_single.blit(text, place)

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
                pygame.draw.rect(screen_single, self.tank.color, (self.bullet_x, self.bullet_y, self.bullet_width, self.bullet_height))
            if self.direction == Direction.LEFT:
                pygame.draw.rect(screen_single, self.tank.color, (self.bullet_x - self.bullet_width, self.bullet_y, self.bullet_width, self.bullet_height))
            if self.direction == Direction.UP:
                pygame.draw.rect(screen_single, self.tank.color, (self.bullet_x, self.bullet_y - self.bullet_height, self.bullet_width, self.bullet_height))
            if self.direction == Direction.DOWN:
                pygame.draw.rect(screen_single, self.tank.color, (self.bullet_x, self.bullet_y, self.bullet_width, self.bullet_height))      

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
        pygame.draw.rect(screen_single,(219,65,22),(self.x,self.y,self.width,self.height))
    
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
        pygame.draw.circle(screen_single, (14,196,199), (self.x,self.y), self.radius)
        pygame.draw.line(screen_single,(255,255,255),(399,490),(399,510), 2)
        pygame.draw.line(screen_single,(255,255,255),(399,490),(392,500), 2)
        pygame.draw.line(screen_single,(255,255,255),(399,490),(406,500), 2)
        
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

        screen_single.fill((0,0,0))
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
            screen_single.blit(text, place)
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
            screen_single.blit(text, place) 
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
                screen_single.blit(text, place)                    

                font1 = pygame.font.Font('freesansbold.ttf', 30)
                text1 = font1.render("Press [ESC] to Exit", 1, (0,22,255))
                place1 = text1.get_rect(center = (400, 335))
                screen_single.blit(text1, place1)

                font2 = pygame.font.Font('freesansbold.ttf', 30)
                text2 = font2.render("Press [R] to Restart", 1, (0,22,255))
                place2 = text2.get_rect(center = (400, 375))
                screen_single.blit(text2, place2)
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




screen_online = pygame.display.set_mode((1100,600))

class TankRPC:
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host = ip,
                port = RabbitPort,
                virtual_host = vhost,
                credentials = credents
            )
        )
        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue = '', auto_delete = True, exclusive = True)
        self.queue_callback = result.method.queue

        self.channel.queue_bind(exchange = 'X:routing.topic',
                                queue = self.queue_callback)

        self.channel.basic_consume(
            queue = self.queue_callback,
            on_message_callback = self.callback,
            auto_ack = True
        )

        self.response = None
        self.corr_id = None
        self.token = None
        self.tankid = None
        self.roomid = None
        
    
    def callback(self, ch, method, properties, body):
        if self.corr_id == properties.correlation_id:
            self.response = json.loads(body)
            print(self.response)

    def call(self, rout_key, message = {}):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange = 'X:routing.topic',
            routing_key = rout_key,
            properties = pika.BasicProperties(
                reply_to = self.queue_callback,
                correlation_id = self.corr_id,
            ),
            body=json.dumps(message)
        ) 
        while self.response is None:
            self.connection.process_data_events()

    def server_check(self):
        self.call('tank.request.healthcheck')
        if self.response['status'] == '200':
            return True
        return False


    def register(self, room_id):
        message = {
            'roomId': room_id
        }
        self.call('tank.request.register', message)
        if 'token' in self.response:
            self.token = self.response['token']
            self.tankid = self.response['tankId']
            
            return True
        return False
    
    def povorot(self, token, direction):
        message = {
            'token': token,
            'direction': direction
        }
        self.call('tank.request.turn', message)

    def vistrel(self, token):
        message = {
            'token': token
        }
        self.call('tank.request.fire', message)

class ConsumeDataTanks(Thread):
    def __init__(self, room_id):
        super().__init__()
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host = ip,
                port = RabbitPort,
                virtual_host = vhost,
                credentials = credents
            )
        )
        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue = '', auto_delete = True, exclusive = True)
        self.queue_callback = result.method.queue
        

        self.channel.queue_bind(exchange = 'X:routing.topic', queue = self.queue_callback, routing_key = 'event.state.' + room_id)
        
        self.channel.basic_consume(
            queue = self.queue_callback,
            on_message_callback = self.callback,
            auto_ack = True
        )
        
        self.response = None
    
    def callback(self, ch, method, properties, body):
        self.response = json.loads(body)
        print(self.response)

    def run(self):
        self.channel.start_consuming()

class Smert:
    def __init__(self):
        self.death = False
        self.score = 0
        self.smert2 = False

    def death_ekran(self):   
        
        def blit_text(txt, x, y, FontSize, color):
            font = pygame.font.Font('freesansbold.ttf', FontSize)
            text = font.render(txt, 1, color)
            place = text.get_rect(center=(x, y))
            screen_online.blit(text, place)

        def blit_screen_online():
            pygame.draw.rect(screen_online, (0,0,0), (0,0,1100,600))
            blit_text('BETTER LUCK NEXT TIME :(', 550,180, 40, (255,223,0))
            blit_text("Restart [R]", 550, 280, 30, (255,0,0))
            blit_text("Exit to MAIN MENU [ESC]", 550, 360, 30, (255,0,0))
            blit_text('Your Score: ' + str(self.score), 900, 500, 40, (255,223,0))
        

        run = True

        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                    if event.key == pygame.K_r:
                        run = False
                        game_online()
                        self.death = False
                        self.smert2 = False

            blit_screen_online()
            pygame.display.flip()

class Pobeda:
    def __init__(self):
        self.vigral = False
        self.score = 0
    
    def win_ekran(self):

        def blit_text(txt, x, y, FontSize, color):
            font = pygame.font.Font('freesansbold.ttf', FontSize)
            text = font.render(txt, 1, color)
            place = text.get_rect(center=(x, y))
            screen_online.blit(text, place)

        def blit_screen_online():
            pygame.draw.rect(screen_online, (0,0,0), (0,0,1100,600))
            blit_text('WINNER WINNER CHICKEN DINNER!!!', 550,180, 40, (255,223,0))
            blit_text("Restart [R]", 550, 280, 30, (255,0,0))
            blit_text("Exit to MAIN MENU [ESC]", 550, 360, 30, (255,0,0))
            blit_text('Your Score: ' + str(self.score), 900, 500, 40, (255,223,0))

        run = True

        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                    if event.key == pygame.K_r:
                        run = False
                        game_online()
                        self.vigral = False

            blit_screen_online()
            pygame.display.flip()

class Kicked:
    def __init__(self):
        self.kicket = False
        self.score = 0
    
    def kick_ekran(self):
        def blit_text(txt, x, y, FontSize, color):
            font = pygame.font.Font('freesansbold.ttf', FontSize)
            text = font.render(txt, 1, color)
            place = text.get_rect(center=(x, y))
            screen_online.blit(text, place)

        def blit_screen_online():
            pygame.draw.rect(screen_online, (0,0,0), (0,0,1100,600))
            blit_text('SINCE YOU WERE AFK, YOU WERE KICKED', 550,180, 40, (255,223,0))
            blit_text("Restart [R]", 550, 280, 30, (255,0,0))
            blit_text("Exit to MAIN MENU [ESC]", 550, 360, 30, (255,0,0))
            blit_text('Your Score: ' + str(self.score), 900, 500, 40, (255,223,0))

        run = True

        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                    if event.key == pygame.K_r:
                        run = False
                        game_online()
                        self.kicket = False

            blit_screen_online()
            pygame.display.flip()


UP = 'UP'
DOWN = 'DOWN'
RIGHT = 'RIGHT'
LEFT = 'LEFT'

TURN_KEYS = {
    pygame.K_w: UP,
    pygame.K_a: LEFT,
    pygame.K_s: DOWN,
    pygame.K_d: RIGHT
}

def game_online():
    client = TankRPC()

    client.server_check()
    client.register('room-1')
    

    event_collect = ConsumeDataTanks('room-1')

    event_collect.start()
    

    mixer.music.play(-1)
    def blit_text(txt, x, y, FontSize, color):
        font = pygame.font.Font('freesansbold.ttf', FontSize)
        text = font.render(txt, 1, color)
        place = text.get_rect(center=(x, y))
        screen_online.blit(text, place)

    def draw_tanks(x, y, width, height, direction, color_tank):
        tank_center = (x + width // 2, y + height // 2)        

        pygame.draw.rect(screen_online, color_tank, (x, y, width, height), 6)
        pygame.draw.circle(screen_online, color_tank, tank_center, width // 2,4)
        if direction == 'RIGHT':
            pygame.draw.line(screen_online, color_tank, 
                             (tank_center[0] + width // 2, tank_center[1]), (x + width + width // 2, y + height // 2), 4)
        if direction == 'LEFT':
            pygame.draw.line(screen_online, color_tank, 
                             (tank_center[0] - width // 2, tank_center[1]), (x - width // 2, y + height // 2), 4)
        if direction == 'UP':
            pygame.draw.line(screen_online, color_tank, 
                             (tank_center[0], tank_center[1] - width // 2), (x + width // 2, y - height // 2), 4)
        if direction == 'DOWN':
            pygame.draw.line(screen_online, color_tank, 
                             (tank_center[0], tank_center[1] + width // 2), (x + width // 2, y + height + height // 2), 4)
    
    def draw_bullets(x, y, width, height, color_bullet):
        pygame.draw.rect(
            screen_online, color_bullet,
            (x, y, width, height)
        )

    def rand_color():
        R = random.randint(20,225)
        G = random.randint(20,128)
        B = random.randint(20,225)
        color_enemy = (R,G,B)
        return color_enemy

    TANKS = {}

    hp = 3
    ochko = 0

    is_game = True
    remain = True

    smert = Smert()
    pobeda = Pobeda()
    kicked = Kicked()

    while is_game:
        screen_online.fill((0,0,0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_game = False
                mixer.music.stop()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    is_game = False
                    mixer.music.stop()
                
                if event.key in TURN_KEYS:
                    client.povorot(client.token, TURN_KEYS[event.key])
                
                if event.key == pygame.K_SPACE:
                    client.vistrel(client.token)
                    self_shot.play()


        tanks = event_collect.response['gameField']['tanks']
        try:
            rem_time = event_collect.response['remainingTime']
        except:
            pass
        bullets = event_collect.response['gameField']['bullets']
        hits = event_collect.response['hits']
        winners = event_collect.response['winners']
        losers = event_collect.response['losers']
        kickers = event_collect.response['kicked']

        for winner in winners:
            if client.tankid == winner['tankId']:
                pobeda.vigral = True
                is_game = False
                pobeda.score = winner['score']
                mixer.music.stop()
                self_win.play()
    
        for loser in losers:
            if client.tankid == loser['tankId']:
                smert.death = True
                is_game = False
                smert.score = loser['score']
                mixer.music.stop()
                self_dead.play()

        for kicker in kickers:
            if client.tankid == kicker['tankId']:
                kicked.kicket = True
                is_game = False
                kicked.score = kicker['score']
                mixer.music.stop() 
                self_kicked.play()

        if rem_time == 10 and remain:
            out_of_time.play()
            remain = False

        for tank in tanks:
            if client.tankid != tank['id']:
                if not TANKS.get(tank['id']):
                    TANKS[tank['id']] = rand_color()
        
        tank_num = 0

        for tank in tanks:
            
            if client.tankid == tank['id']:
                draw_tanks(tank['x'], tank['y'], tank['width'],tank['height'], tank['direction'], (35,187,17))
            else:
                tank_num += 1
                draw_tanks(tank['x'], tank['y'], tank['width'],tank['height'], tank['direction'], TANKS[tank['id']])
            
            
            if client.tankid == tank['id']:
                if tank['health'] < hp:
                    hit_self.play()
                    hp = tank['health']
    
        pygame.draw.rect(screen_online, (4,104,115), (800, 0, 300, 600))
        
        blit_text("Remaining Time: {}".format(rem_time), 950, 530, 24, (255,255,255))
        g = len(tanks) - 1
        f = g
        t = 0
        blit_text("My Tank          Health           Score", 950, 30, 14, (255,255,255))
        blit_text("Enemy Tanks       Health           Score", 950, 80, 14, (255,255,255))

        for tank in tanks:
            if client.tankid == tank['id']:                
                blit_text(tank['id'] + "           " + str(tank['health']) + "               " + str(tank['score']), 940,50,17, (35,187,17))
                ochko = tank['score']
            else:
                blit_text(tank['id'] + "             " + str(tank['health']) + "                 " + str(tank['score']), 950,100 + (20 * t),17, TANKS[tank['id']])
                t += 1
                if f == 0:
                    t = 0
                    f = g
                f -= 1

        if tank_num + 1 != len(tanks):
            is_game = False
            smert.smert2 = True
            smert.score = ochko

        for bullet in bullets:
            if client.tankid == bullet['owner']:
                draw_bullets(bullet['x'], bullet['y'], bullet['width'], bullet['height'], (35,187,17))
            else:
                draw_bullets(bullet['x'], bullet['y'], bullet['width'], bullet['height'], TANKS[bullet['owner']])

        for hit in hits:
            if client.tankid == hit['source']:
                shot_enemy.play()
            if client.tankid != hit['source'] and client.tankid != hit['destination']:
                other_hit.play()

        pygame.display.flip()
    
    if kicked.kicket == True:
        kicked.kick_ekran()
    elif pobeda.vigral == True:
        pobeda.win_ekran()
    elif smert.death == True:
        smert.death_ekran()
    elif smert.smert2 == True:
        smert.death_ekran()




screen_online_ai = pygame.display.set_mode((1100,600))

# class TankRPC:
#     def __init__(self):
#         self.connection = pika.BlockingConnection(
#             pika.ConnectionParameters(
#                 host = ip,
#                 port = RabbitPort,
#                 virtual_host = vhost,
#                 credentials = credents
#             )
#         )
#         self.channel = self.connection.channel()

#         result = self.channel.queue_declare(queue = '', auto_delete = True, exclusive = True)
#         self.queue_callback = result.method.queue

#         self.channel.queue_bind(exchange = 'X:routing.topic',
#                                 queue = self.queue_callback)

#         self.channel.basic_consume(
#             queue = self.queue_callback,
#             on_message_callback = self.callback,
#             auto_ack = True
#         )

#         self.response = None
#         self.corr_id = None
#         self.token = None
#         self.tankid = None
#         self.roomid = None
        
    
#     def callback(self, ch, method, properties, body):
#         if self.corr_id == properties.correlation_id:
#             self.response = json.loads(body)
#             print(self.response)

#     def call(self, rout_key, message = {}):
#         self.response = None
#         self.corr_id = str(uuid.uuid4())
#         self.channel.basic_publish(
#             exchange = 'X:routing.topic',
#             routing_key = rout_key,
#             properties = pika.BasicProperties(
#                 reply_to = self.queue_callback,
#                 correlation_id = self.corr_id,
#             ),
#             body=json.dumps(message)
#         ) 
#         while self.response is None:
#             self.connection.process_data_events()

#     def server_check(self):
#         self.call('tank.request.healthcheck')
#         if self.response['status'] == '200':
#             return True
#         return False


#     def register(self, room_id):
#         message = {
#             'roomId': room_id
#         }
#         self.call('tank.request.register', message)
#         if 'token' in self.response:
#             self.token = self.response['token']
#             self.tankid = self.response['tankId']
            
#             return True
#         return False
    
#     def povorot(self, token, direction):
#         message = {
#             'token': token,
#             'direction': direction
#         }
#         self.call('tank.request.turn', message)

#     def vistrel(self, token):
#         message = {
#             'token': token
#         }
#         self.call('tank.request.fire', message)

# class ConsumeDataTanks(Thread):
#     def __init__(self, room_id):
#         super().__init__()
#         self.connection = pika.BlockingConnection(
#             pika.ConnectionParameters(
#                 host = ip,
#                 port = RabbitPort,
#                 virtual_host = vhost,
#                 credentials = credents
#             )
#         )
#         self.channel = self.connection.channel()

#         result = self.channel.queue_declare(queue = '', auto_delete = True, exclusive = True)
#         self.queue_callback = result.method.queue
        

#         self.channel.queue_bind(exchange = 'X:routing.topic', queue = self.queue_callback, routing_key = 'event.state.' + room_id)
        
#         self.channel.basic_consume(
#             queue = self.queue_callback,
#             on_message_callback = self.callback,
#             auto_ack = True
#         )
        
#         self.response = None
    
#     def callback(self, ch, method, properties, body):
#         self.response = json.loads(body)
#         print(self.response)

#     def run(self):
#         self.channel.start_consuming()

class Smert_ai:
    def __init__(self):
        self.death = False
        self.score = 0
        self.smert_ai2 = False

    def death_ekran(self):   
        
        def blit_text(txt, x, y, FontSize, color):
            font = pygame.font.Font('freesansbold.ttf', FontSize)
            text = font.render(txt, 1, color)
            place = text.get_rect(center=(x, y))
            screen_online_ai.blit(text, place)

        def blit_screen_online_ai():
            pygame.draw.rect(screen_online_ai, (0,0,0), (0,0,1100,600))
            blit_text('BETTER LUCK NEXT TIME :(', 550,180, 40, (255,223,0))
            blit_text("Restart [R]", 550, 280, 30, (255,0,0))
            blit_text("Exit to MAIN MENU [ESC]", 550, 360, 30, (255,0,0))
            blit_text('Your Score: ' + str(self.score), 900, 500, 40, (255,223,0))
        

        run = True

        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                    if event.key == pygame.K_r:
                        run = False
                        game_online()
                        self.death = False

            blit_screen_online_ai()
            pygame.display.flip()

class Pobeda_ai:
    def __init__(self):
        self.vigral = False
        self.score = 0
    
    def win_ekran(self):

        def blit_text(txt, x, y, FontSize, color):
            font = pygame.font.Font('freesansbold.ttf', FontSize)
            text = font.render(txt, 1, color)
            place = text.get_rect(center=(x, y))
            screen_online_ai.blit(text, place)

        def blit_screen_online_ai():
            pygame.draw.rect(screen_online_ai, (0,0,0), (0,0,1100,600))
            blit_text('WINNER WINNER CHICKEN DINNER!!!', 550,180, 40, (255,223,0))
            blit_text("Restart [R]", 550, 280, 30, (255,0,0))
            blit_text("Exit to MAIN MENU [ESC]", 550, 360, 30, (255,0,0))
            blit_text('Your Score: ' + str(self.score), 900, 500, 40, (255,223,0))

        run = True

        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                    if event.key == pygame.K_r:
                        run = False
                        game_online()
                        self.vigral = False

            blit_screen_online_ai()
            pygame.display.flip()

class Kicked_ai:
    def __init__(self):
        self.kicket = False
        self.score = 0
    
    def kick_ekran(self):
        def blit_text(txt, x, y, FontSize, color):
            font = pygame.font.Font('freesansbold.ttf', FontSize)
            text = font.render(txt, 1, color)
            place = text.get_rect(center=(x, y))
            screen_online_ai.blit(text, place)

        def blit_screen_online_ai():
            pygame.draw.rect(screen_online_ai, (0,0,0), (0,0,1100,600))
            blit_text('SINCE YOU WERE AFK, YOU WERE KICKED', 550,180, 40, (255,223,0))
            blit_text("Restart [R]", 550, 280, 30, (255,0,0))
            blit_text("Exit to MAIN MENU [ESC]", 550, 360, 30, (255,0,0))
            blit_text('Your Score: ' + str(self.score), 900, 500, 40, (255,223,0))

        run = True

        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                    if event.key == pygame.K_r:
                        run = False
                        game_online()
                        self.kicket = False

            blit_screen_online_ai()
            pygame.display.flip()

def game_online_ai():
    client = TankRPC()

    client.server_check()
    client.register('room-1')
    

    event_collect = ConsumeDataTanks('room-1')

    event_collect.start()
    client.povorot(client.token, 'UP')

    def blit_text(txt, x, y, FontSize, color):
        font = pygame.font.Font('freesansbold.ttf', FontSize)
        text = font.render(txt, 1, color)
        place = text.get_rect(center=(x, y))
        screen_online_ai.blit(text, place)

    def draw_tanks(x, y, width, height, direction, color_tank):
        tank_center = (x + width // 2, y + height // 2)        

        pygame.draw.rect(screen_online_ai, color_tank, (x, y, width, height), 6)
        pygame.draw.circle(screen_online_ai, color_tank, tank_center, width // 2,4)
        if direction == 'RIGHT':
            pygame.draw.line(screen_online_ai, color_tank, 
                             (tank_center[0] + width // 2, tank_center[1]), (x + width + width // 2, y + height // 2), 4)
        if direction == 'LEFT':
            pygame.draw.line(screen_online_ai, color_tank, 
                             (tank_center[0] - width // 2, tank_center[1]), (x - width // 2, y + height // 2), 4)
        if direction == 'UP':
            pygame.draw.line(screen_online_ai, color_tank, 
                             (tank_center[0], tank_center[1] - width // 2), (x + width // 2, y - height // 2), 4)
        if direction == 'DOWN':
            pygame.draw.line(screen_online_ai, color_tank, 
                             (tank_center[0], tank_center[1] + width // 2), (x + width // 2, y + height + height // 2), 4)
    
    def draw_bullets(x, y, width, height, color_bullet):
        pygame.draw.rect(
            screen_online_ai, color_bullet,
            (x, y, width, height)
        )

    def rand_color():
        R = random.randint(20,225)
        G = random.randint(20,128)
        B = random.randint(20,225)
        color_enemy = (R,G,B)
        return color_enemy

    TANKS = {}
    BULLETS_X = {}
    BULLETS_Y = {}
    BULLETS_DIR = {}
    TANKS_X = {}
    TANKS_Y = {}
    TANKS_DIR = {}

    my_x = 0
    my_y = 0
    my_width = 31
    my_direction = ''
    time_afk = 120
    ochko = 0

    hp = 3

    is_game = True
    remain = True

    smert_ai = Smert_ai()
    pobeda_ai = Pobeda_ai()
    kicked_ai = Kicked_ai()

    while is_game:
        screen_online_ai.fill((0,0,0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_game = False
                mixer.music.stop()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    is_game = False
                    mixer.music.stop()

        tanks = event_collect.response['gameField']['tanks']
        try:
            rem_time = event_collect.response['remainingTime']
        except:
            pass
        bullets = event_collect.response['gameField']['bullets']
        hits = event_collect.response['hits']
        winners = event_collect.response['winners']
        losers = event_collect.response['losers']
        kickers = event_collect.response['kicked']

        for tank in tanks:
            if client.tankid == tank['id']:
                my_x = tank['x']
                my_y = tank['y']
                my_width = 31
                my_direction = tank['direction']
            else:
                TANKS_X[tank['id']] = tank['x']
                TANKS_Y[tank['id']] = tank['y']
                TANKS_DIR[tank['id']] = tank['direction']
        
        for bullet in bullets:
            if client.tankid != bullet['owner']:
                BULLETS_X[bullet['owner']] = bullet['x']
                BULLETS_Y[bullet['owner']] = bullet['y']
                BULLETS_DIR[bullet['owner']] = bullet['direction']


        for bullet in BULLETS_X:
            if abs(int(BULLETS_X[bullet] - my_x)) <= 31:
                if BULLETS_DIR[bullet] == 'DOWN' and my_direction == 'DOWN':
                    client.povorot(client.token, 'LEFT')
                    time_afk = rem_time
                if BULLETS_DIR[bullet] == 'DOWN' and my_direction == 'UP':
                    client.povorot(client.token, 'RIGHT')
                    time_afk = rem_time
                if BULLETS_DIR[bullet] == 'UP' and my_direction == 'UP':
                    client.povorot(client.token, 'RIGHT')
                    time_afk = rem_time
                if BULLETS_DIR[bullet] == 'UP' and my_direction == 'DOWN':
                    client.povorot(client.token, 'LEFT')
                    time_afk = rem_time
                
            
            if my_direction == 'DOWN' and BULLETS_DIR[bullet] == 'LEFT':
                if abs(abs(BULLETS_X[bullet] - my_x) - abs(BULLETS_Y[bullet] - my_y) // 2.5) <= 12:
                    client.povorot(client.token, 'RIGHT')
            if my_direction == 'DOWN' and BULLETS_DIR[bullet] == 'RIGHT':
                if abs(abs(BULLETS_X[bullet] - my_x) - abs(BULLETS_Y[bullet] - my_y) // 2.5) <= 12:
                    client.povorot(client.token, 'RIGHT')
            if my_direction == 'UP' and BULLETS_DIR[bullet] == 'LEFT':
                if abs(abs(BULLETS_X[bullet] - my_x) - abs(BULLETS_Y[bullet] - my_y) // 2.5) <= 12:
                    client.povorot(client.token, 'RIGHT')
            if my_direction == 'UP' and BULLETS_DIR[bullet] == 'RIGHT':
                if abs(abs(BULLETS_X[bullet] - my_x) - abs(BULLETS_Y[bullet] - my_y) // 2.5) <= 12:
                    client.povorot(client.token, 'LEFT')


        for bullet in BULLETS_Y:
            if abs(int(BULLETS_Y[bullet] - my_y)) <= 31:
                if BULLETS_DIR[bullet] == 'LEFT' and my_direction == 'LEFT':
                    client.povorot(client.token, 'UP')
                    time_afk = rem_time
                if BULLETS_DIR[bullet] == 'LEFT' and my_direction == 'RIGHT':
                    client.povorot(client.token, 'DOWN')
                    time_afk = rem_time
                if BULLETS_DIR[bullet] == 'RIGHT' and my_direction == 'RIGHT':
                    client.povorot(client.token, 'DOWN')
                    time_afk = rem_time
                if BULLETS_DIR[bullet] == 'RIGHT' and my_direction == 'LEFT':
                    client.povorot(client.token, 'UP')
                    time_afk = rem_time
            
            if my_direction == 'LEFT' and BULLETS_DIR[bullet] == 'UP':
                if abs(abs(BULLETS_Y[bullet] - my_y) - abs(BULLETS_X[bullet] - my_x) // 2.5) <= 12:
                    client.povorot(client.token, 'DOWN')
            if my_direction == 'LEFT' and BULLETS_DIR[bullet] == 'DOWN':
                if abs(abs(BULLETS_Y[bullet] - my_y) - abs(BULLETS_X[bullet] - my_x) // 2.5) <= 12:
                    client.povorot(client.token, 'UP')
            if my_direction == 'RIGHT' and BULLETS_DIR[bullet] == 'UP':
                if abs(abs(BULLETS_Y[bullet] - my_y) - abs(BULLETS_X[bullet] - my_x) // 2.5) <= 12:
                    client.povorot(client.token, 'DOWN')
            if my_direction == 'RIGHT' and BULLETS_DIR[bullet] == 'DOWN':
                if abs(abs(BULLETS_Y[bullet] - my_y) - abs(BULLETS_X[bullet] - my_x) // 2.5) <= 12:
                    client.povorot(client.token, 'UP')

        for tank in TANKS_X:
            if my_direction == "DOWN" and TANKS_DIR[tank] == "RIGHT":
                if abs(abs(TANKS_X[tank] - my_x) - abs(TANKS_Y[tank] - my_y) // 2.5) <= 12:
                    self_shot.play()
                    client.vistrel(client.token)
                    time_afk = rem_time
            if my_direction == "DOWN" and TANKS_DIR[tank] == "LEFT":
                if abs(abs(TANKS_X[tank] - my_x) - abs(TANKS_Y[tank] - my_y) // 2.5) <= 12:
                    self_shot.play()
                    client.vistrel(client.token)
                    time_afk = rem_time
            
            if my_direction == "UP" and TANKS_DIR[tank] == "RIGHT":
                if abs(abs(TANKS_X[tank] - my_x) - abs(TANKS_Y[tank] - my_y) // 2.5) <= 12:
                    self_shot.play()
                    client.vistrel(client.token)
                    time_afk = rem_time
            if my_direction == "UP" and TANKS_DIR[tank] == "LEFT":
                if abs(abs(TANKS_X[tank] - my_x) - abs(TANKS_Y[tank] - my_y) // 2.5) <= 12:
                    self_shot.play()
                    client.vistrel(client.token)
                    time_afk = rem_time
            
            if my_direction == "LEFT" and TANKS_DIR[tank] == "UP":
                if abs(abs(TANKS_Y[tank] - my_y) - abs(TANKS_X[tank] - my_x) // 2.5) <= 12:
                    self_shot.play()
                    client.vistrel(client.token)
                    time_afk = rem_time
            if my_direction == "LEFT" and TANKS_DIR[tank] == "DOWN":
                if abs(abs(TANKS_Y[tank] - my_y) - abs(TANKS_X[tank] - my_x) // 2.5) <= 12:
                    self_shot.play()
                    client.vistrel(client.token)
                    time_afk = rem_time
            
            if my_direction == "RIGHT" and TANKS_DIR[tank] == "UP":
                if abs(abs(TANKS_Y[tank] - my_y) - abs(TANKS_X[tank] - my_x) // 2.5) <= 12:
                    self_shot.play()
                    client.vistrel(client.token)
                    time_afk = rem_time
            if my_direction == "RIGHT" and TANKS_DIR[tank] == "DOWN":
                if abs(abs(TANKS_Y[tank] - my_y) - abs(TANKS_X[tank] - my_x) // 2.5) <= 12:
                    self_shot.play()
                    client.vistrel(client.token)
                    time_afk = rem_time
            
            if my_direction == 'DOWN' and TANKS_DIR[tank] == 'DOWN':
                if abs(TANKS_X[tank] - my_x) <= 31:
                    self_shot.play()
                    client.vistrel(client.token)
                    time_afk = rem_time

            if my_direction == 'UP' and TANKS_DIR[tank] == 'UP':
                if abs(TANKS_X[tank] - my_x) <= 31:
                    self_shot.play()
                    client.vistrel(client.token)
                    time_afk = rem_time

            if my_direction == 'LEFT' and TANKS_DIR[tank] == 'LEFT':
                if abs(TANKS_Y[tank] - my_y) <= 31:
                    self_shot.play()
                    client.vistrel(client.token)
                    time_afk = rem_time

            if my_direction == 'RIGHT' and TANKS_DIR[tank] == 'RIGHT':
                if abs(TANKS_Y[tank] - my_y) <= 31:
                    self_shot.play()
                    client.vistrel(client.token)
                    time_afk = rem_time    

        for winner in winners:
            if client.tankid == winner['tankId']:
                pobeda_ai.vigral = True
                is_game = False
                mixer.music.stop()
                self_win_ai.play()
                pobeda_ai.score = winner['score']
    
        for loser in losers:
            if client.tankid == loser['tankId']:
                smert_ai.death = True
                is_game = False
                mixer.music.stop()
                self_dead_ai.play()
                smert_ai.score = loser['score']

        for kicker in kickers:
            if client.tankid == kicker['tankId']:
                kicked_ai.kicket = True
                is_game = False
                mixer.music.stop() 
                self_kicked_ai.play()
                kicked_ai.score = kicker['score']

        if abs(time_afk - rem_time) >= 25:
            client.povorot(client.token, my_direction)
            time_afk = rem_time

        if rem_time == 10 and remain:
            out_of_time.play()
            remain = False

        for tank in tanks:
            if client.tankid != tank['id']:
                if not TANKS.get(tank['id']):
                    TANKS[tank['id']] = rand_color()
        
        tank_num = 0
        
        for tank in tanks:
            
            if client.tankid == tank['id']:
                draw_tanks(tank['x'], tank['y'], tank['width'],tank['height'], tank['direction'], (35,187,17))
            else:
                tank_num += 1
                draw_tanks(tank['x'], tank['y'], tank['width'],tank['height'], tank['direction'], TANKS[tank['id']])
            
            
            if client.tankid == tank['id']:
                if tank['health'] < hp:
                    hit_self.play()
                    hp = tank['health']
    
        pygame.draw.rect(screen_online_ai, (4,104,115), (800, 0, 300, 600))
        
        blit_text("Remaining Time: {}".format(rem_time), 950, 530, 24, (255,255,255))
        g = len(tanks) - 1
        f = g
        t = 0
        blit_text("My Tank          Health           Score", 950, 30, 14, (255,255,255))
        blit_text("Enemy Tanks       Health           Score", 950, 80, 14, (255,255,255))

        for tank in tanks:
            if client.tankid == tank['id']:                
                blit_text(tank['id'] + "           " + str(tank['health']) + "               " + str(tank['score']), 940,50,17, (35,187,17))
                ochko = tank['score']
            else:
                blit_text(tank['id'] + "             " + str(tank['health']) + "                 " + str(tank['score']), 950,100 + (20 * t),17, TANKS[tank['id']])
                t += 1
                if f == 0:
                    t = 0
                    f = g
                f -= 1
            
        if tank_num + 1 != len(tanks) and pobeda_ai.vigral != True:
            is_game = False
            smert_ai.smert_ai2 = True
            smert_ai.score = ochko
            mixer.music.stop()
            self_dead_ai.play()

        for bullet in bullets:
            if client.tankid == bullet['owner']:
                draw_bullets(bullet['x'], bullet['y'], bullet['width'], bullet['height'], (35,187,17))
            else:
                draw_bullets(bullet['x'], bullet['y'], bullet['width'], bullet['height'], TANKS[bullet['owner']])

        for hit in hits:
            if client.tankid == hit['source']:
                shot_enemy.play()
            if client.tankid != hit['source'] and client.tankid != hit['destination']:
                other_hit.play()

        pygame.display.flip()
    
    if kicked_ai.kicket == True:
        kicked_ai.kick_ekran()
    elif pobeda_ai.vigral == True:
        pobeda_ai.win_ekran()
    elif smert_ai.death == True:
        smert_ai.death_ekran()
    elif smert_ai.smert_ai2 == True:
        smert_ai.death_ekran()






# МЕНЮ ГЛАВНОГО ЭКРАНА
def main_screen():
    font = pygame.font.Font('freesansbold.ttf', 30)     
    text = font.render("WELCOME TO TANKS GAME", 1, (22,110,199)) 
    place = text.get_rect(center = (550,120))   
    screen.blit(text, place)

    font2 = pygame.font.Font('freesansbold.ttf', 15)     
    text2 = font2.render("Press [SPACE] to start a single player", 1, (22,110,199)) 
    place2 = text2.get_rect(center = (550,200))   
    screen.blit(text2, place2)

    font3 = pygame.font.Font('freesansbold.ttf', 15)     
    text3 = font3.render("Press [M] to start a multiplayer", 1, (22,110,199)) 
    place3 = text3.get_rect(center = (550,230))   
    screen.blit(text3, place3)

    font4 = pygame.font.Font('freesansbold.ttf', 15)
    text4 = font4.render("Press [I] to start a multiplayer via AI", 1, (22,110,199))
    place4 = text4.get_rect(center = (550,260))
    screen.blit(text4,place4)

running = True
# ЗАПУСКАЕТСЯ ГЛАВНАЯ ПРОГРАММА
mixer.music.play(-1)
while running:

    screen.fill((255,255,255))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            # ЕСЛИ МЫ НАЖИМАЕМ НА ESC, ТО ПРОГРАММА ЗАКРЫВАЕТСЯ
            if event.key == pygame.K_ESCAPE:
                running = False
                pygame.quit()
                sys.exit()
                

            # ЕСЛИ ЖЕ НА ПРОБЕЛ, ТО ЗАПУСКАЕТСЯ КОД ТАНКОВ
            if event.key == pygame.K_SPACE:
                igra()
            
            if event.key == pygame.K_m:
                game_online()

            if event.key == pygame.K_i:
                game_online_ai()

    # ВЫВОДИМ ГЛАВНЫЙ ЭКРАН
    main_screen()


    # ОБНОВЛЯЕМ ЭКРАН ИГРЫ :)
    pygame.display.flip()
