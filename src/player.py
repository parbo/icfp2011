import sys

from state import LEFT_APPLICATION, RIGHT_APPLICATION

class Player(object):
    def __init__(self, first):
        self.first = first
        
    def play(self):
        if self.first:
            self.write_move(LEFT_APPLICATION, 'I', 0)
            self.read_move()
        else:
            self.read_move()
            self.write_move(LEFT_APPLICATION, 'I', 0)
    
    def make_move(self, direction, card_name, slot_ix):
        pass
    
    def write_move(self, direction, card_name, slot_ix):
        print direction
        if direction == LEFT_APPLICATION:
            print card_name
            print slot_ix
        else:
            print slot_ix
            print card_name
        
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
    