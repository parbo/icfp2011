#!/usr/bin/python
import sys

from common import LEFT_APPLICATION, RIGHT_APPLICATION
from state import State
from command import Command
from strategy import SimpleAttacker, SimpleDefender

class Player(object):
    def __init__(self, first):
        self.first = first
        self.player = State()
        self.opponent = State()
        self.player.opponent = self.opponent
        self.opponent.opponent = self.player
        self.cmd = Command(self.player)
        if self.first:
            self.strategy = SimpleAttacker(self.player, self.opponent, self.cmd)
        else:
            self.strategy = SimpleDefender(self.player, self.opponent, self.cmd)
        
    def play(self):
        if self.first:
            self.player_move()
            self.opponent_move()
        else:
            self.opponent_move()
            self.player_move()
    
    def player_move(self):
        self.player.apply_zombies()
        move = self.strategy.move()
        self.player.application(*move)
        self.write_move(*move)

    def opponent_move(self):
        move = self.read_move()
        self.opponent.apply_zombies()
        self.opponent.application(*move)
    
    def write_move(self, direction, card_name, slot_ix):
        print direction
        if direction == LEFT_APPLICATION:
            print card_name
            print slot_ix
        else:
            print slot_ix
            print card_name
        sys.stdout.flush()
        
    def read_move(self):
        direction = sys.stdin.readline().strip()
        if direction == LEFT_APPLICATION:
            card_name = sys.stdin.readline().strip()
            slot_ix = int(sys.stdin.readline().strip())
        else:
            slot_ix = int(sys.stdin.readline().strip())
            card_name = sys.stdin.readline().strip()
        return (direction, card_name, slot_ix)
        
def play(first_player):
    player = Player(first_player)
    while True:
        player.play()
        
if __name__ == '__main__':
    first_player = (sys.argv[1] == '0')
    play(first_player)

