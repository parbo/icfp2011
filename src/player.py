#!/usr/bin/python
import sys

from state import LEFT_APPLICATION, RIGHT_APPLICATION, State

class Player(object):
    def __init__(self, first):
        self.first = first
        self.player = State()
        self.opponent = State()
        self.player.opponent = self.opponent
        self.opponent.opponent = self.player
        
    def play(self):
        if self.first:
            self.player_move(LEFT_APPLICATION, 'I', 0)
            self.opponent_move()
        else:
            self.opponent_move()
            self.player_move(LEFT_APPLICATION, 'I', 0)
    
    def player_move(self, direction, card_name, slot_ix):
        self.player.apply_zombies()
        self.player.application(direction, card_name, slot_ix)
        self.write_move(LEFT_APPLICATION, 'I', 0)

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

