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
    def __init__(self, *args, **kwargs):
        super(ClientUpdate, self).__init__(*args, **kwargs)

    def _closest_player(self):
        # closest = sorted(client.players.values(), key=lambda p:p.dist_from(me))[0]
        me = client.player
        distance = 1e6
        closest = None
        for player in client.players.values():
            if player == me:
                continue
            d = me.dist_from(player)
            if d < distance:
                distance = d
                closest = player

        return closest, distance

    def run(self):

        FULL_TURN = 1.5

        while not self.wait():
            if not client.connected:
                continue

            # respawn as mohawk
            mohawk = str(ship_types['Mohawk'])
            packet = packets.build_player_command('COMMAND', com='respawn', data=mohawk)
            client.send(packet)

            me = client.player

            closest, distance = self._closest_player()
            if distance < 800:
                print(f'closest: {closest} ({distance})')

            self.wait(2)

            # client.key('LEFT', True)
            # self.wait(FULL_TURN)
            # client.key('LEFT', False)


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
