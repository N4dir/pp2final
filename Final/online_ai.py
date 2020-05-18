import pika
import uuid
import json
import pygame
import random
from threading import Thread
from pygame import mixer

pygame.init()

mixer.music.load('Music_online/bg_online.wav')

hit_self = mixer.Sound('Music_online/hit_self.wav')
shot_enemy = mixer.Sound('Music_online/shot_enemy.wav')
other_hit = mixer.Sound('Music_online/other_hit.wav')
self_dead = mixer.Sound('Music_online/self_dead.wav')
self_win = mixer.Sound('Music_online/self_win.wav')
out_of_time = mixer.Sound('Music_online/out_of_time.wav')
self_shot = mixer.Sound('Music_online/self_shot.wav')
self_kicked = mixer.Sound('Music_online/self_kicked.wav')

ip = '34.254.177.17'
RabbitPort = '5672'
vhost = 'dar-tanks'
credents = pika.PlainCredentials(username = 'dar-tanks', password ='5orPLExUYnyVYZg48caMpX')


screen = pygame.display.set_mode((1100,600))

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
            screen.blit(text, place)

        def blit_screen():
            pygame.draw.rect(screen, (0,0,0), (0,0,1100,600))
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

            blit_screen()
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
            screen.blit(text, place)

        def blit_screen():
            pygame.draw.rect(screen, (0,0,0), (0,0,1100,600))
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

            blit_screen()
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
            screen.blit(text, place)

        def blit_screen():
            pygame.draw.rect(screen, (0,0,0), (0,0,1100,600))
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

            blit_screen()
            pygame.display.flip()

def game_online_ai():
    client = TankRPC()

    client.server_check()
    client.register('room-1')
    

    event_collect = ConsumeDataTanks('room-1')

    event_collect.start()
    client.povorot(client.token, 'UP')

    mixer.music.play(-1)
    def blit_text(txt, x, y, FontSize, color):
        font = pygame.font.Font('freesansbold.ttf', FontSize)
        text = font.render(txt, 1, color)
        place = text.get_rect(center=(x, y))
        screen.blit(text, place)

    def draw_tanks(x, y, width, height, direction, color_tank):
        tank_center = (x + width // 2, y + height // 2)        

        pygame.draw.rect(screen, color_tank, (x, y, width, height), 6)
        pygame.draw.circle(screen, color_tank, tank_center, width // 2,4)
        if direction == 'RIGHT':
            pygame.draw.line(screen, color_tank, 
                             (tank_center[0] + width // 2, tank_center[1]), (x + width + width // 2, y + height // 2), 4)
        if direction == 'LEFT':
            pygame.draw.line(screen, color_tank, 
                             (tank_center[0] - width // 2, tank_center[1]), (x - width // 2, y + height // 2), 4)
        if direction == 'UP':
            pygame.draw.line(screen, color_tank, 
                             (tank_center[0], tank_center[1] - width // 2), (x + width // 2, y - height // 2), 4)
        if direction == 'DOWN':
            pygame.draw.line(screen, color_tank, 
                             (tank_center[0], tank_center[1] + width // 2), (x + width // 2, y + height + height // 2), 4)
    
    def draw_bullets(x, y, width, height, color_bullet):
        pygame.draw.rect(
            screen, color_bullet,
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

    smert = Smert()
    pobeda = Pobeda()
    kicked = Kicked()

    while is_game:
        screen.fill((0,0,0))
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
                if BULLETS_DIR[bullet] == 'UP' and my_direction == 'UP':
                    client.povorot(client.token, 'RIGHT')
                    time_afk = rem_time
                if BULLETS_DIR[bullet] == 'UP' and my_direction == 'DOWN':
                    client.povorot(client.token, 'LEFT')
                    time_afk = rem_time
                if BULLETS_DIR[bullet] == 'DOWN' and my_direction == 'DOWN':
                    client.povorot(client.token, 'LEFT')
                    time_afk = rem_time
                if BULLETS_DIR[bullet] == 'DOWN' and my_direction == 'UP':
                    client.povorot(client.token, 'RIGHT')
                    time_afk = rem_time
                
            if my_direction == 'UP' and BULLETS_DIR[bullet] == 'LEFT':
                if abs(abs(BULLETS_X[bullet] - my_x) - abs(BULLETS_Y[bullet] - my_y) // 2.5) <= 12:
                    client.povorot(client.token, 'RIGHT')
            if my_direction == 'UP' and BULLETS_DIR[bullet] == 'RIGHT':
                if abs(abs(BULLETS_X[bullet] - my_x) - abs(BULLETS_Y[bullet] - my_y) // 2.5) <= 12:
                    client.povorot(client.token, 'LEFT')
            if my_direction == 'DOWN' and BULLETS_DIR[bullet] == 'LEFT':
                if abs(abs(BULLETS_X[bullet] - my_x) - abs(BULLETS_Y[bullet] - my_y) // 2.5) <= 12:
                    client.povorot(client.token, 'RIGHT')
            if my_direction == 'DOWN' and BULLETS_DIR[bullet] == 'RIGHT':
                if abs(abs(BULLETS_X[bullet] - my_x) - abs(BULLETS_Y[bullet] - my_y) // 2.5) <= 12:
                    client.povorot(client.token, 'RIGHT')


        for bullet in BULLETS_Y:
            if abs(int(BULLETS_Y[bullet] - my_y)) <= 31:
                if BULLETS_DIR[bullet] == 'RIGHT' and my_direction == 'RIGHT':
                    client.povorot(client.token, 'DOWN')
                    time_afk = rem_time
                if BULLETS_DIR[bullet] == 'RIGHT' and my_direction == 'LEFT':
                    client.povorot(client.token, 'UP')
                    time_afk = rem_time
                if BULLETS_DIR[bullet] == 'LEFT' and my_direction == 'LEFT':
                    client.povorot(client.token, 'UP')
                    time_afk = rem_time
                if BULLETS_DIR[bullet] == 'LEFT' and my_direction == 'RIGHT':
                    client.povorot(client.token, 'DOWN')
                    time_afk = rem_time
            
            if my_direction == 'RIGHT' and BULLETS_DIR[bullet] == 'UP':
                if abs(abs(BULLETS_Y[bullet] - my_y) - abs(BULLETS_X[bullet] - my_x) // 2.5) <= 12:
                    client.povorot(client.token, 'DOWN')
            if my_direction == 'RIGHT' and BULLETS_DIR[bullet] == 'DOWN':
                if abs(abs(BULLETS_Y[bullet] - my_y) - abs(BULLETS_X[bullet] - my_x) // 2.5) <= 12:
                    client.povorot(client.token, 'UP')
            if my_direction == 'LEFT' and BULLETS_DIR[bullet] == 'UP':
                if abs(abs(BULLETS_Y[bullet] - my_y) - abs(BULLETS_X[bullet] - my_x) // 2.5) <= 12:
                    client.povorot(client.token, 'DOWN')
            if my_direction == 'LEFT' and BULLETS_DIR[bullet] == 'DOWN':
                if abs(abs(BULLETS_Y[bullet] - my_y) - abs(BULLETS_X[bullet] - my_x) // 2.5) <= 12:
                    client.povorot(client.token, 'UP')

        for tank in TANKS_X:
            if my_direction == "UP" and TANKS_DIR[tank] == "RIGHT":
                if abs(abs(TANKS_X[tank] - my_x) - abs(TANKS_Y[tank] - my_y) // 2.5) <= 12:
                    client.vistrel(client.token)
                    time_afk = rem_time
            if my_direction == "UP" and TANKS_DIR[tank] == "LEFT":
                if abs(abs(TANKS_X[tank] - my_x) - abs(TANKS_Y[tank] - my_y) // 2.5) <= 12:
                    client.vistrel(client.token)
                    time_afk = rem_time
            
            if my_direction == "DOWN" and TANKS_DIR[tank] == "RIGHT":
                if abs(abs(TANKS_X[tank] - my_x) - abs(TANKS_Y[tank] - my_y) // 2.5) <= 12:
                    client.vistrel(client.token)
                    time_afk = rem_time
            if my_direction == "DOWN" and TANKS_DIR[tank] == "LEFT":
                if abs(abs(TANKS_X[tank] - my_x) - abs(TANKS_Y[tank] - my_y) // 2.5) <= 12:
                    client.vistrel(client.token)
                    time_afk = rem_time
            
            if my_direction == "RIGHT" and TANKS_DIR[tank] == "UP":
                if abs(abs(TANKS_Y[tank] - my_y) - abs(TANKS_X[tank] - my_x) // 2.5) <= 12:
                    client.vistrel(client.token)
                    time_afk = rem_time
            if my_direction == "RIGHT" and TANKS_DIR[tank] == "DOWN":
                if abs(abs(TANKS_Y[tank] - my_y) - abs(TANKS_X[tank] - my_x) // 2.5) <= 12:
                    client.vistrel(client.token)
                    time_afk = rem_time

            if my_direction == "LEFT" and TANKS_DIR[tank] == "UP":
                if abs(abs(TANKS_Y[tank] - my_y) - abs(TANKS_X[tank] - my_x) // 2.5) <= 12:
                    client.vistrel(client.token)
                    time_afk = rem_time
            if my_direction == "LEFT" and TANKS_DIR[tank] == "DOWN":
                if abs(abs(TANKS_Y[tank] - my_y) - abs(TANKS_X[tank] - my_x) // 2.5) <= 12:
                    client.vistrel(client.token)
                    time_afk = rem_time
            
            if my_direction == 'UP' and TANKS_DIR[tank] == 'UP':
                if abs(TANKS_X[tank] - my_x) <= 31:
                    client.vistrel(client.token)
                    time_afk = rem_time

            if my_direction == 'DOWN' and TANKS_DIR[tank] == 'DOWN':
                if abs(TANKS_X[tank] - my_x) <= 31:
                    client.vistrel(client.token)
                    time_afk = rem_time

            if my_direction == 'RIGHT' and TANKS_DIR[tank] == 'RIGHT':
                if abs(TANKS_Y[tank] - my_y) <= 31:
                    client.vistrel(client.token)
                    time_afk = rem_time
                
            if my_direction == 'LEFT' and TANKS_DIR[tank] == 'LEFT':
                if abs(TANKS_Y[tank] - my_y) <= 31:
                    client.vistrel(client.token)
                    time_afk = rem_time

        if abs(time_afk - rem_time) >= 25:
            client.povorot(client.token, my_direction)
            time_afk = rem_time

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
    
        pygame.draw.rect(screen, (4,104,115), (800, 0, 300, 600))
        
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
