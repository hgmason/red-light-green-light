import random
import math
import pygame
from pygame import mixer
import time

import sys
import os

def resource_path(relative_path):
    try:
    # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

pygame.init()
mixer.init()
mixer.music.load(resource_path("song.mp3"))

pygame.display.set_caption('the hibiscus flower has bloomed')
screen_height = 500; screen_width = 700
screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()
FPS = 30  # Frames per second

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (100, 200, 255)
YELLOW = (255, 255, 0)

class Player:
    def __init__(self, pos = None, color = (255, 100, 255), speed = None, confidence = None):
        if pos is None:
            pos = [random.randint(0, screen_width-1), int(screen_height*.9) + random.randint(0, int(screen_height*.1))]
        if confidence == None:
            confidence = random.randint(60,100)/100
        if speed == None:
            speed = random.choice([i/6 for i in range(3,7)])

        self.color = color
        self.size = 6 #height and width of bounding box
        self.pos = pos
        self.confidence = confidence
        self.speed = speed
        self.alive = True
        self.moving = True
        self.want_threshold = .995
        return
    def sigmoid(self, x):
        return 1/(1 + math.exp(-x))
    def choose_move(self, doll, move = True):
        if self.alive:
            if doll.looking:
                wants_to_move = random.random() > self.want_threshold
                self.want_threshold = self.want_threshold + .000001
                #print(self.want_threshold)
            else:
                wants_to_move = True
            if wants_to_move:
                xdel = 2*(random.random() - .5)*self.speed/3
                ymag = (.8 + (random.random()*.2))*self.speed
                ydir = random.choices([1,0,-1], weights = [(1 - self.confidence)/4, (1 - self.confidence)*3/4, self.confidence])[0]
                ydel = ymag*ydir
            else:
                xdel = 0
                ydel = 0
            if move:
                self.move(xdel, ydel)
            return [xdel, ydel]
        else:
            return [0,0]
    def move(self, xdelta, ydelta):
        if xdelta == 0 and ydelta == 0:
            self.moving = False
        else:
            self.moving = True
        self.pos[0] = self.pos[0] + xdelta
        self.pos[1] = self.pos[1] + ydelta

        if self.pos[0] < 0:
            self.pos[0] = 0
        if self.pos[1] < 0:
            self.pos[1] = 0
        if self.pos[0] > screen_width:
            self.pos[0] = screen_width
        if self.pos[1] > screen_height:
            self.pos[1] = screen_height
        return
    def die(self):
        self.alive = False
        self.moving = False
        self.color = RED
        global num_alive
        num_alive = num_alive - 1
        return
    def draw(self):
        pygame.draw.circle(screen, self.color, self.pos, self.size/2)
        return

class MainCharacter(Player):
    def __init__(self, pos = None, color = (255, 100, 255), speed = None, confidence = None):
        Player.__init__(self, pos, color, speed, confidence)
        self.size = self.size*2
        self.speed = self.speed * 1.01

    def choose_move(self, doll, move = True):
        if self.alive:
            xdel = current_x*self.speed
            ydel = current_y*self.speed
            if move:
                self.move(xdel, ydel)

class Doll:
    def __init__(self, pos = [screen_width//2, 20], speed = 15, view = 60, view_range = 2000, freq = .55, cycle = 320, color = YELLOW):
        self.pos = pos
        self.speed = speed
        self.view = view
        self.range = view_range
        self.angle = 270
        self.freq = freq #amount of time spent looking forward =
        self.cycle = cycle #num of ticks in a full cycle
        self.size = 20
        self.color = color
        self.sight_color = (0,100,0)
        self.sight = [(0,0), (0,0), (0,0)]
        self.looking = False

        self.pos[1] = self.pos[1] + self.size//2

        self.time_forward = int(self.freq*self.cycle)
        self.time_back = self.cycle - self.time_forward
        self.forward_count = 0
        self.backward_count = 0
        self.dir = 1 #1 = back, 2 = foward, -1 = moving to back, -2 moving to forward
        self.forward_dir = 1
        self.float_cycle = self.cycle

        self.draw_all()
        mixer.music.play()
        return
    def draw_all(self):
        self.draw_sight()
        self.draw()
        return
    def draw(self):
        pygame.draw.circle(screen, self.color, self.pos, self.size/2)
        return
    def sin(self, x):
        return math.sin(x*math.pi/180)
    def cos(self, x):
        return math.cos(x*math.pi/180)
    def draw_sight(self):
        unitxL = self.cos(self.angle-self.view)
        unityL = self.sin(self.angle-self.view)
        unitxR = self.cos(self.angle+self.view)
        unityR = self.sin(self.angle+self.view)
        left = [self.pos[0]+unitxL*self.range,self.pos[1]+unityL*self.range]
        right = [self.pos[0]+unitxR*self.range,self.pos[1]+unityR*self.range]
        points = [self.pos, left, right]
        pygame.draw.polygon(surface=screen, color=self.sight_color,points=points)
        self.sight = points
        return
    def sign(self, p1, p2, p3):
        return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])
    def sees(self, player):
        #check if player pos is inside self.sight
        d1 = self.sign(player.pos, self.sight[0], self.sight[1])
        d2 = self.sign(player.pos, self.sight[1], self.sight[2])
        d3 = self.sign(player.pos, self.sight[2], self.sight[0])

        has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
        has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)

        is_not_over = (not end.is_over(player))
        can_see = not (has_neg and has_pos) and is_not_over and player.moving and self.looking

        if can_see:
            self.shoot(player)
        return
    def shoot(self, player):
        #tell the player that they're dead
        player.die()
        #draw the player
        #draw the gun line
        #update the screen
        #erase the line
        return
    def update(self):

        self.time_forward = int(self.freq*self.cycle)
        self.time_back = self.cycle - self.time_forward

        #increment the counts if it's standing still
        if self.dir == 1:
            self.backward_count += 1
            if self.backward_count > self.time_back:
                self.dir = -2
                self.backward_count = 0
                self.sight_color = (100,0,0)
                self.looking = True
        elif self.dir == 2:
            self.view = 20
            #self.angle = random.randint(0,180)
            #self.angle = self.angle + 2*(random.random() - .5)*40
            self.angle = self.angle + self.speed*self.forward_dir*1.2
            if self.angle < 0:
                self.angle = 0
                self.forward_dir = 1
            elif self.angle > 180:
                self.angle = 180
                self.forward_dir = -1
            self.forward_count += 1
            if self.forward_count > self.time_forward:
                self.dir = -1
                self.forward_count = 0
                self.view = 60

        #check if it's moving, and if so, move it
        if self.dir == -1 or self.dir == -2:
            self.angle = (self.angle + self.speed)%360
            if self.dir == -1 and (self.angle > 270):
                self.dir = 1
                self.angle = 270
                self.sight_color = (0,100,0)
                self.looking = False
                mixer.music.play()
            elif self.dir == -2 and (self.angle > 90) and (self.angle < 200):
                self.dir = 2
                self.angle = 90

        #self.float_cycle = self.float_cycle*.999
        #self.cycle = int(self.float_cycle) + 1

        #print(self.cycle)

        #print(self.looking)

        self.draw()
        self.draw_sight()
        return

class HLine:
    def __init__(self, val, dir = 1):
        self.val = val
        self.left = (0, val)
        self.right = (screen_width, val)
        self.dir = dir
    def draw(self):
        pygame.draw.line(screen, WHITE, self.left, self.right, width = 5)
        return
    def is_over(self, player):
        return(self.dir*player.pos[1] < self.val)


def run_game():
    global N
    global num_alive
    global current_x
    global current_y
    global end

    start_time = time.time()
    num_frames = 0

    N = 455

    players = [Player() for i in range(N)]
    mc = MainCharacter(color = BLUE)
    players.append(mc)

    doll = Doll()
    start = HLine(int(screen_height*.9), dir = -1)
    end = HLine(20)

    current_x = 0
    current_y = 0

    num_alive = N+1

    myfont = pygame.font.SysFont('Comic Sans MS', 10)

    while True and mc.alive and not end.is_over(mc):
        clock.tick(FPS)
        num_frames = num_frames + 1
        #print(num_frames/(time.time() - start_time), "FPS")
        if (time.time() - start_time) > 5:
            start_time = time.time()
            num_frames = 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w or event.key == pygame.K_UP:
                    current_y = current_y - 1
                elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    current_y = current_y + 1
                elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
                    current_x = current_x - 1
                elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    current_x = current_x + 1
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_w or event.key == pygame.K_UP:
                    current_y = current_y + 1
                elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    current_y = current_y - 1
                elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
                    current_x = current_x + 1
                elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    current_x = current_x - 1

        doll.update()
        for player in players:
            player.choose_move(doll)
            doll.sees(player)
            if end.is_over(player):
                player.color = GREEN

        screen.fill(BLACK)
        end.draw()
        doll.draw_all()
        start.draw()

        for player in players:
            player.draw()

        textsurface = myfont.render('ALIVE: '+str(num_alive), False, WHITE)
        screen.blit(textsurface,(0,0))

        pygame.display.update()  # Or pygame.display.flip()

    if mc.alive:
        myfont = pygame.font.SysFont('Comic Sans MS', 30)
        textsurface = myfont.render('YOU LIVED.', False, WHITE)
        textrect = textsurface.get_rect()
        textrect.center = (screen_width//2, screen_height//2)
        screen.blit(textsurface,textrect)

        myfont = pygame.font.SysFont('Comic Sans MS', 15)
        textsurface = myfont.render(str(N+1-num_alive)+" died. Press SPACE to play again.", False, WHITE)
        textrect = textsurface.get_rect()
        textrect.center = (screen_width//2, screen_height//2+30)
        screen.blit(textsurface,textrect)

    else:
        myfont = pygame.font.SysFont('Comic Sans MS', 30)
        textsurface = myfont.render('YOU DIED.', False, WHITE)
        textrect = textsurface.get_rect()
        textrect.center = (screen_width//2, screen_height//2)
        screen.blit(textsurface,textrect)

        myfont = pygame.font.SysFont('Comic Sans MS', 15)
        textsurface = myfont.render('So did '+str(N+1-num_alive)+" others. Press SPACE to try again.", False, WHITE)
        textrect = textsurface.get_rect()
        textrect.center = (screen_width//2, screen_height//2+30)
        screen.blit(textsurface,textrect)

    pygame.display.update()

    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return

while True:
    run_game()
