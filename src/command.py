from common import LEFT_APPLICATION, RIGHT_APPLICATION
from cards import I

class Command(object):
    """ Generate move sequences from higher level commands. """
    def __init__(self, state):
        self.state = state
        
    def build_integer(self, i):
        """ Return a sequence of integer operations that generates 'i'. """
        op = []
        while i > 0:
            if i % 2 == 1:
                op.append('succ')
                i -= 1
            else:
                op.append('dbl')
                i /= 2
        op.reverse()
        return op
        
    def set_integer(self, slot_ix, i):
        """ Write an integer value to a slot. """
        slot = self.state[slot_ix]
        moves = []
        if not isinstance(slot.field, I):
            moves.append((LEFT_APPLICATION, 'put', slot_ix))
        moves.append((RIGHT_APPLICATION, 'zero', slot_ix))
        moves.extend([(LEFT_APPLICATION, op, slot_ix) for op in self.build_integer(i)])
        return moves
    
    def copy_slot(self, src_ix, tgt_ix):
        """ Copy the value of a slot to another slot. """
        moves = self.set_integer(tgt_ix, src_ix)
        moves.append((LEFT_APPLICATION, 'get', tgt_ix))
        return moves
    
    def append_card(self, slot_ix, c):
        """ Append a card 'c' to a sequence. """
        moves = []
        moves.append((LEFT_APPLICATION, 'K', slot_ix))
        moves.append((LEFT_APPLICATION, 'S', slot_ix))
        moves.append((RIGHT_APPLICATION, c, slot_ix))
        return moves
    
    def append_int_param(self, slot_ix, i):
        """ Append an integer parameter to a sequence. """
        moves = []
        for int_op in reversed(self.build_integer(i)):
            moves.extend(self.append_card(slot_ix, int_op))
        moves.append((RIGHT_APPLICATION, 'zero', slot_ix))
        return moves
    
    def help_slot(self, src_ix, tgt_ix, cmd_ix, n_ix):
        """
        Help the 'tgt_ix' slot from the 'src_ix' slot. 'cmd_ix' is the slot
        where the help command should be executed and 'n_ix' is the slot that
        stores the amount of vitality.
        """
        moves = []
        moves.append((RIGHT_APPLICATION, 'help', cmd_ix))
        moves.extend(self.append_int_param(cmd_ix, src_ix))
        moves.extend(self.append_int_param(cmd_ix, tgt_ix))
        moves.extend(self.append_card(cmd_ix, 'get'))
        moves.extend(self.append_int_param(cmd_ix, n_ix))
        return moves
    
    def attack_slot(self, src_ix, tgt_ix, cmd_ix, n_ix):
        """
        Attack the '255-tgt_ix' slot from the 'src_ix' slot. 'cmd_ix' is the slot
        where the attack command should be executed and 'n_ix' is the slot that
        stores the amount of vitality.
        """
        moves = []
        moves.append((RIGHT_APPLICATION, 'attack', cmd_ix))
        moves.extend(self.append_int_param(cmd_ix, src_ix))
        moves.extend(self.append_int_param(cmd_ix, tgt_ix))
        moves.extend(self.append_card(cmd_ix, 'get'))
        moves.extend(self.append_int_param(cmd_ix, n_ix))
        return moves