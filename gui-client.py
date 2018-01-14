import os
import sys
from threading import Thread
from time import sleep

import pygame

from airmash.client import Client

client = Client(enable_debug=False, enable_chat=False)


@client.on('PLAYER_HIT')
def on_hit(client, message):
    for player in message.players:
        if player.id == client.player.id:
            print("Uh oh! I've been hit!")


@client.on(['MOB_DESPAWN', 'MOB_DESPAWN_COORDS', 'MOB_UPDATE', 'MOB_UPDATE_STATIONARY'])
def md(client, message):
    print(message)


kwargs = dict(
    name='z',
    flag='GB',
    region='eu',
    room='ffa1',
    enable_trace=False
)

t = Thread(target=client.connect, kwargs=kwargs)
t.start()

size = width, height = 900, 1000
black = 0, 0, 0
white = 255, 255, 255
red = 255, 0, 0
green = 0, 255, 0
blue = 0, 0, 255

player_size = 50
projectile_size = 20

os.environ['SDL_VIDEO_WINDOW_POS'] = "0,20"
pygame.init()
font = pygame.font.SysFont('', 20)
clock = pygame.time.Clock()
screen = pygame.display.set_mode(size)

keys = {
    pygame.K_w: 'UP',
    pygame.K_s: 'DOWN',
    pygame.K_a: 'LEFT',
    pygame.K_d: 'RIGHT',
    pygame.K_SPACE: 'FIRE',
    pygame.K_LSHIFT: 'SPECIAL',
}

while not client.connected:
    sleep(0.1)


def draw(items, colour, size=player_size):
    for item in items:
        if not item.online:
            continue
        x = item.posX - me.posX + (width / 2.0)
        y = item.posY - me.posY + (height / 2.0)
        if 0 < x < width and 0 < y < height:
            pygame.draw.rect(screen, colour, (x, y, size, size))
            textsurface = font.render(str(item), True, white)
            screen.blit(textsurface, (x, y))


while 1:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        elif event.type == pygame.KEYDOWN:
            d = keys.get(event.key)
            if d:
                client.key(d, True)

        elif event.type == pygame.KEYUP:
            d = keys.get(event.key)
            if d:
                client.key(d, False)

    screen.fill(black)

    me = client.player
    draw([me], blue)
    draw(client.players.values(), green)
    draw(client.projectiles.values(), red, size=20)

    pygame.display.flip()
    clock.tick(30)
