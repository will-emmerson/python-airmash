import math
import random
import threading

from reloadr import reloadr, autoreload

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


@reloadr
def _evade(self):
    me = client.player
    distance_cutoff = 500  # min distance for me to worry about missile
    angle_cutoff = 0.2  # angle difference
    for p in list(client.projectiles.values()):
        if p.owner == me or not p.online or me.dist_from(p) > distance_cutoff:
            continue
        # if p.id in self.evaded:
        #     print(f'ignoring missile {p.id} from {p.owner} because')
        diff = abs(p.angle_to(me) - p.rotation)
        # TODO: take into account distance
        if diff < angle_cutoff:
            # print(f'own:{p.owner} p_rot:{p.rotation:.1f} p_rot_to_me:{p.angle_to(me)} diff:{diff}')
            # work out best way to evade
            rel = me.angle_to(p) - me.rotation
            pi = math.pi
            if rel < 0:
                rel += pi * 2
            print(f'EVADING {p.owner} speed:{p.speedX},{p.speedY} diff:{diff:.1f}')

            if pi * 0.25 < rel < pi * 0.75 or pi * 1.25 < rel < pi * 1.75:
                print('backwards/forwards')
                direction = random.choice(['DOWN', 'UP'])
                client.key(direction, True)
                self.wait(0.3)
                client.key(direction, False)
            else:
                # strafe
                print('strafe right/left')
                direction = random.choice(['LEFT', 'RIGHT'])
                client.key('SPECIAL', True)
                client.key(direction, True)
                self.wait(0.3)
                client.key(direction, False)
                client.key('SPECIAL', False)



class ClientUpdate(StoppableThread):

    full_turn = 1.5
    # evaded = set()

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

        if closest.name == 'Flaps':
            return

        angle_to_closest = me.angle_to(closest)
        print(f'closest:{closest} ({distance})')
        difference = angle_to_closest - me.rotation
        wait = difference / (2 * math.pi) * full_turn
        print(f'angle:{angle_to_closest:.2f} me:{me.rotation:.2f}')
        print(f'difference:{difference:.2f} wait:{wait:.2f}')

        # TODO: this is wrong as can be negative quite a lot
        # Probably need to just subtract 2pi, or make a normalize function
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

        if distance < 800:
            client.key('FIRE', True)
            self.wait(1)
            client.key('FIRE', False)

            if distance < 500:
                print('retreating')
                client.key('DOWN', True)
                self.wait(1)
                client.key('DOWN', False)

        else:
            print('following')
            client.key('UP', True)
            self.wait(1)
            client.key('UP', False)




    def _respawn_as(self, ship):
        # respawn as mohawk
        mohawk = str(ship_types[ship])
        packet = packets.build_player_command('COMMAND', com='respawn', data=mohawk)
        client.send(packet)


                # self.evaded.add(p.id)

    def run(self):
        while not client.connected:
            self.wait(0.1)
        self._respawn_as('Mohawk')

        while not self.wait():

            # _evade._reload()
            _evade(self)
            self._shoot_closest_player()
            # me = client.player
            # direction = 'LEFT'
            # client.key(direction, True)
            # self.wait(self.full_turn / 4.0)
            # client.key(direction, False)
            # client.key('FIRE', True)
            # client.key('FIRE', False)
            # self.wait(0.2)
            # p = list(filter(lambda x: x.owner == me, client.projectiles.values()))[0]
            # print(f'rot:{p.rotation}')
            # diff = p.angle_to(me) - p.rotation
            # print(f'p_rot:{p.rotation:.1f} p_rot_to_me:{p.angle_to(me)} diff:{diff}')
            # # print(math.atan2(p.speedX, -p.speedY))
            # #
            # break
            # self._evade()
            # self.wait(1)
            # self._shoot_closest_player()


# ClientUpdate._start_timer_reload(1)

def track_position(player, key, old, new):
    new = [int(x) for x in new]
    print("Position: {} {}".format(*new))


def track_rotation(player, key, old, new):
    print("Rotation: {}".format(new))


client = Client(enable_debug=False)


# @client.on('LOGIN')
# def on_login(client, message):
    # print("Client has logged in!")
    # print("Player ID: {}".format(client.player.id))
    # client.player.on_change('position', track_position)
    # client.player.on_change('rotation', track_rotation)


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
