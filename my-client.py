import math
import threading

from airmash import packets
from airmash.client import Client
from airmash.types import ship_types


class StoppableThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._event = threading.Event()

    def stop(self):
        self._event.set()

    def wait(self, timeout=1.0):
        return self._event.wait(timeout=timeout)


class ClientUpdate(StoppableThread):

    full_turn = 1.5

    def __init__(self, *args, **kwargs):
        super(ClientUpdate, self).__init__(*args, **kwargs)

    def _closest_player(self):
        # closest = sorted(client.players.values(), key=lambda p:p.dist_from(me))[0]
        me = client.player
        distance = 1e6
        closest = None
        for player in client.players.values():
            if player == me or not player.online:
                continue
            d = me.dist_from(player)
            if d < distance:
                distance = d
                closest = player

        return closest, distance

    def _shoot_closest_player(self):
        full_turn = self.full_turn
        half_turn = full_turn / 2.0
        me = client.player

        closest, distance = self._closest_player()
        if distance < 800:

            angle_to_closest = me.angle_to(closest)
            print(f'closest:{closest} ({distance})')
            difference = angle_to_closest - me.rotation
            wait = difference / (2 * math.pi) * full_turn
            print(f'angle:{angle_to_closest:.2f} me:{me.rotation:.2f}')
            print(f'difference:{difference:.2f} wait:{wait:.2f}')

            direction = 'RIGHT'
            if wait < 0:
                direction = 'LEFT'
                wait = -wait
            elif wait > half_turn:
                direction = 'LEFT'
                wait = full_turn - wait

            print(f'new wait:{wait:.2f} ({direction})')
            print()

            client.key(direction, True)
            self.wait(wait)
            client.key(direction, False)

            client.key('FIRE', True)
            client.key('FIRE', False)

    def _evade(self):
        me = client.player
        cutoff = 500
        for p in client.projectiles.values():
            # if p.owner == me or not p.online or me.dist_from(p) > cutoff:
            #     continue
            print(f'rot:{p.rotation:.1f} owner:{p.owner} distance:{me.dist_from(p):.1f} x:{p.posX} y:{p.posY}')



    def run(self):
        self.wait(1)

        # respawn as mohawk
        mohawk = str(ship_types['Mohawk'])
        packet = packets.build_player_command('COMMAND', com='respawn', data=mohawk)
        client.send(packet)

        while not self.wait():
            if not client.connected:
                continue

            me = client.player
            client.key('FIRE', True)
            client.key('FIRE', False)
            self.wait(0.2)
            p = list(filter(lambda x: x.owner == me, client.projectiles.values()))[0]
            print(f'projectile:{p.posX},{p.posY}')

            break
            # self._evade()
            # self.wait(1)
            # self._shoot_closest_player()




def track_position(player, key, old, new):
    new = [int(x) for x in new]
    print("Position: {} {}".format(*new))


def track_rotation(player, key, old, new):
    print("Rotation: {}".format(new))


client = Client(enable_debug=False)


@client.on('LOGIN')
def on_login(client, message):
    print("Client has logged in!")
    print("Player ID: {}".format(client.player.id))
    client.player.on_change('position', track_position)
    client.player.on_change('rotation', track_rotation)


@client.on('PLAYER_HIT')
def on_hit(client, message):
    for player in message.players:
        if player.id == client.player.id:
            print("Uh oh! I've been hit!")


_t_update = ClientUpdate()
_t_update.start()

client.connect(
    name='z',
    flag='GB',
    region='eu',
    room='ffa1',
    enable_trace=False
)

_t_update.stop()
_t_update.join()
