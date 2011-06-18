from common import MAX_VITALITY

class Strategy(object):
    def __init__(self, player, opponent, cmd):
        self.player = player
        self.opponent = opponent
        self.cmd = cmd
        self.current_move_seq = []
        
    def move(self):
        if not self.current_move_seq:
            self.current_move_seq = list(reversed(self.next_move_seq()))
        return self.current_move_seq.pop()
        
    def strongest_slot(self, state):
        slot_ix = None
        max_vitality = 0
        for ix, slot in enumerate(state.slots):
            if slot.vitality > max_vitality:
                max_vitality = slot.vitality
                slot_ix = ix
        return slot_ix
    
    def weakest_slot(self, state):
        slot_ix = None
        min_vitality = MAX_VITALITY + 1
        for ix, slot in enumerate(state.slots):
            if slot.vitality < min_vitality:
                min_vitality = slot.vitality
                slot_ix = ix
        return slot_ix
    
class AttackStrategy(Strategy):
    def __init__(self, player, opponent, cmd):
        Strategy.__init__(self, player, opponent, cmd)
        self.init = True
        
    def next_move_seq(self):
        if self.init:
            self.init = False
            return self.cmd.set_integer(1, 1024)
        else:
            weakest = self.weakest_slot(self.opponent)
            strongest = self.strongest_slot(self.player)
            return self.cmd.attack_slot(strongest, weakest, 0, 1)
        
class DefenceStrategy(Strategy):
    def __init__(self, player, opponent, cmd):
        Strategy.__init__(self, player, opponent, cmd)
        self.init = True
        
    def next_move_seq(self):
        if self.init:
            self.init = False
            return self.cmd.set_integer(1, 1024)
        else:
            weakest = self.weakest_slot(self.player)
            strongest = self.strongest_slot(self.player)
            return self.cmd.help_slot(strongest, weakest, 0, 1)