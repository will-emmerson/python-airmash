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


kwargs = dict(
    name='z',
    flag='GB',
    region='eu',
    room='ffa1',
    enable_trace=False
)

t = Thread(target=client.connect, kwargs=kwargs)
t.start()


size = width, height = 1000, 800
black = 0, 0, 0
white = 255, 255, 255
red = 255, 0, 0
green = 0, 255, 0
blue = 0, 0, 255
player_size = 50

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
    for player in list(client.players.values()):
        if not player.online:
            continue
        x = player.posX - me.posX + (width / 2.0)
        y = player.posY - me.posY + (height / 2.0)
        if 0 < x < width and 0 < y < height:
            colour = blue if player == me else green
            pygame.draw.rect(screen, colour, (x, y, player_size, player_size))
            textsurface = font.render(player.name, False, white)
            screen.blit(textsurface, (x, y))

    for projectile in list(client.projectiles.values()):
        if not projectile.online:
            continue
        x = projectile.posX - me.posX + (width / 2.0)
        y = projectile.posY - me.posY + (height / 2.0)
        if 0 < x < width and 0 < y < height:
            pygame.draw.rect(screen, red, (x, y, 20, 20))
            label = f'{projectile.speedX:.1f} {projectile.accelX:.1f}'
            # print(label)
            textsurface = font.render(label, False, white)
            screen.blit(textsurface, (x, y))

    pygame.display.flip()
    clock.tick(30)
