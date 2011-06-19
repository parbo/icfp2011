from common import NBR_OF_SLOTS, MAX_VITALITY

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
        
    def get_register(self, min_ix=0):
        """ Return the index of a slot that can be used as a command register. """
        for ix, slot in enumerate(self.player.slots):
            if (ix >= min_ix) and slot.alive:
                return ix
        return 0
        
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
            if slot.alive and (slot.vitality < min_vitality):
                min_vitality = slot.vitality
                slot_ix = ix
        return slot_ix
    
    def dead_slots(self, state):
        return [ix for ix, s in enumerate(state.slots) if not s.alive]
        
    def attack_value(self, target_vitality):
        target_vitality *= 10
        return target_vitality / 9 + target_vitality % 9
    
class SimpleAttacker(Strategy):
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
            return self.cmd.attack_slot(strongest, 255 - weakest, 0, 1)
        
class SimpleDefender(Strategy):
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
            
class AttackWeakest(Strategy):
    def __init__(self, player, opponent, cmd):
        Strategy.__init__(self, player, opponent, cmd)
        self.attack_margin = 10
        
    def next_move_seq(self):
        # Revive dead slots.
        dead_slots = self.dead_slots(self.player)
        if dead_slots:
            return self.cmd.revive_slot(dead_slots[0], self.get_register())
            
        # Look for a target to attack.
        weakest = self.weakest_slot(self.opponent)
        strongest = self.strongest_slot(self.player)
        attack_value = self.attack_value(self.opponent[weakest].vitality)
        
        if self.player[strongest].vitality - self.attack_margin > attack_value:
            cmd_reg = self.get_register()
            value_reg = self.get_register(cmd_reg + 1)
            moves = self.cmd.set_integer(value_reg, attack_value)
            moves.extend(self.cmd.attack_slot(strongest, 255 - weakest, cmd_reg, value_reg))
            return moves
        
        # Build vitality.
        src = self.get_vitality_src()
        vitality_transfer = self.player[src].vitality / 2
        cmd_reg = self.get_register()
        value_reg = self.get_register(cmd_reg + 1)
        moves = self.cmd.set_integer(value_reg, vitality_transfer)
        moves.extend(self.cmd.attack_slot(src, strongest, cmd_reg, value_reg))
        return moves
    
    def get_vitality_src(self):
        slots = [(s.vitality, ix) for ix, s in enumerate(self.player.slots)]
        slots.sort()
        return slots[NBR_OF_SLOTS / 2][1]