from common import NBR_OF_SLOTS, MAX_SLOT_IDX, DEFAULT_VITALITY, MAX_VITALITY
from common import Error, NotAlive, InvalidSlot
from cards import Function, I, card, CARDS

LEFT_APPLICATION = '1'
RIGHT_APPLICATION = '2'

class State(object):
    def __init__(self):
        self.slots = [Slot() for ix in range(NBR_OF_SLOTS)]
        self.turn = 0
        self.opponent = None
        self.zombie_appl = False
        # 'result' member is used for test purposes.
        self.result = None
        
    def __getitem__(self, key):
        if (key < 0) or (key > MAX_SLOT_IDX):
            raise InvalidSlot('Invalid slot number (%d)' % key)
        return self.slots[key]
        
    def application(self, direction, card, slot):
        self.turn += 1
        result = None
        Function.calls = 0
        try:
            if not slot.alive:
                raise NotAlive
            if direction == LEFT_APPLICATION:
                result = card(self, slot.field)
            else:
                result = slot.field(self, card)
        except (Error, TypeError) as error:
            #print 'Error:', error
            slot.field = I()
            self.result = error
        else:
            slot.field = result
            self.result = result
        
    def left_appl(self, card_name, slot_idx):
        self.application(LEFT_APPLICATION, card(card_name), self.slots[slot_idx])
        
    def right_appl(self, card_name, slot_idx):
        self.application(RIGHT_APPLICATION, card(card_name), self.slots[slot_idx])
        
    def apply_zombies(self):
        self.zombie_appl = True
        for slot in self.slots:
            if slot.vitality < 0:
                try:
                    slot.field(I())
                except (Error, TypeError) as error:
                    pass
                finally:
                    slot.field = I()
                    slot.vitality = 0
        self.zombie_appl = False        
        
class Slot(object):
    def __init__(self, field=I(), vitality=DEFAULT_VITALITY):
        self.field = field
        self.vitality = vitality
        
    def __str__(self):
        return '{%d,%s}' % (self.vitality, self.field)
        
    @property
    def alive(self):
        return self.vitality > 0
    
    def increase(self, dv):
        """ Increase the vitality of the slot. """
        self.vitality += dv
        if self.vitality > MAX_VITALITY:
            self.vitality = MAX_VITALITY
    
    def decrease(self, dv):
        """ Decrease the vitality of the slot. """
        self.vitality -= dv
        if self.vitality < 0:
            self.vitality = 0
    
def test():
    state = State()
    for slot_ix, card_name in enumerate(CARDS.iterkeys()):
        state.right_appl(card_name, slot_ix)
    for slot_ix in range(len(CARDS)):
        print '%d=%s' % (slot_ix, state.slots[slot_ix])
    
if __name__ == '__main__':
    test()