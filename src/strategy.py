from common import NBR_OF_SLOTS, MAX_SLOT_IDX, MAX_VITALITY

class Strategy(object):
    def __init__(self, player, opponent, cmd):
        self.player = player
        self.opponent = opponent
        self.cmd = cmd
        self.current_move_seq = []
        self.assigned_registers = set()
        self.min_register_vitality = 2
        
    def move(self):
        if not self.current_move_seq:
            self.current_move_seq = list(reversed(self.next_move_seq()))
        return self.current_move_seq.pop()
        
    def move_done(self):
        if isinstance(self.player.result, Exception):
            # Abort sequence after error.
            self.current_move_seq = []
        
    def get_register(self, min_ix=0):
        """ Return the index of a slot that can be used as a command register. """
        for ix, slot in enumerate(self.player.slots):
            if (ix >= min_ix) and slot.vitality >= self.min_register_vitality and (ix not in self.assigned_registers):
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
        
    def weak_slots(self, state):
        return [ix for ix, s in enumerate(state.slots) if s.vitality == 1]
        
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
            return self.cmd.attack_slot(strongest, MAX_SLOT_IDX - weakest, 0, 1)
        
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
            
class Cache(object):
    def __init__(self, strategy, player, cmd):
        self.strategy = strategy
        self.player = player
        self.cmd = cmd
        self.src_ref = None
        self.tgt_ref = None
        self.val_ref = None
        self.cmd_ix = None
        #self.cmd_cache = None
        self.sequence_terminator = None
        
    def is_valid(self):
        #for slot_ix in (self.src_ref, self.tgt_ref, self.val_ref, self.cmd_ix, self.cmd_cache):
        for slot_ix in (self.src_ref, self.tgt_ref, self.val_ref, self.cmd_ix):
            if (slot_ix is None) or (not self.player[slot_ix].alive):
                return False
        return True
    
    def invalidate(self):
        #for slot_ix in (self.src_ref, self.tgt_ref, self.val_ref, self.cmd_ix, self.cmd_cache):
        for slot_ix in (self.src_ref, self.tgt_ref, self.val_ref, self.cmd_ix):
            self.strategy.assigned_registers.discard(slot_ix)
        self.src_ref = None
        self.tgt_ref = None
        self.val_ref = None
        self.cmd_ix = None
        #self.cmd_cache = None
        
    def assign_registers(self):
        self.src_ref = self.strategy.get_register(0)
        self.strategy.assigned_registers.add(self.src_ref)
        self.tgt_ref = self.strategy.get_register(self.src_ref)
        self.strategy.assigned_registers.add(self.tgt_ref)
        self.val_ref = self.strategy.get_register(self.tgt_ref)
        self.strategy.assigned_registers.add(self.val_ref)
        self.cmd_ix = self.strategy.get_register(self.val_ref)
        self.strategy.assigned_registers.add(self.cmd_ix)
        #self.cmd_cache = self.strategy.get_register(self.cmd_ix)
        #self.strategy.assigned_registers.add(self.cmd_cache)
                
    def load_registers(self, src_ix, tgt_ix, value):
        moves = []
        if self.player[self.src_ref].field != src_ix:
            moves.extend(self.cmd.set_integer(self.src_ref, src_ix))
        if self.player[self.tgt_ref].field != tgt_ix:
            moves.extend(self.cmd.set_integer(self.tgt_ref, tgt_ix))
        if self.player[self.val_ref].field != value:
            moves.extend(self.cmd.set_integer(self.val_ref, value))
        return moves
    
    def store_cmd(self):
        return self.cmd.copy_slot(self.cmd_ix, self.cmd_cache)
        
    def load_cmd(self):
        return self.cmd.copy_slot(self.cmd_cache, self.cmd_ix)
    
    def attack_moves(self):
        moves = self.cmd.attack_slot_ref(self.src_ref, self.tgt_ref, self.cmd_ix, self.val_ref)
        self.sequence_terminator = moves[-1]
        return moves
        
    def help_moves(self):
        moves = self.cmd.help_slot_ref(self.src_ref, self.tgt_ref, self.cmd_ix, self.val_ref)
        self.sequence_terminator = moves[-1]
        return moves
    
    def cmd_terminator(self):
        return self.sequence_terminator
            
class AttackWeakest(Strategy):
    def __init__(self, player, opponent, cmd):
        Strategy.__init__(self, player, opponent, cmd)
        self.attack_margin = 10
        self.attack_cache = Cache(self, player, cmd)
        self.help_cache = Cache(self, player, cmd)
        
    def next_move_seq(self):
        # Revive dead slots.
        dead_slots = self.dead_slots(self.player)
        if dead_slots:
            return self.cmd.revive_slot(dead_slots[0], self.get_register())
            
        # Decrease slots with vitality=1.
        weak_slots = self.weak_slots(self.opponent)
        if weak_slots:
            return self.cmd.dec_slot(MAX_SLOT_IDX - weak_slots[0], self.get_register())
            
        # Look for a target to attack.
        #weakest = self.weakest_slot(self.opponent)
        target = self.select_target()
        strongest = self.strongest_slot(self.player)
        attack_value = self.attack_value(self.opponent[target].vitality)
        moves = []
        
        if self.player[strongest].vitality - self.attack_margin > attack_value:
            if self.attack_cache.is_valid():
                moves.extend(self.attack_cache.load_registers(strongest, MAX_SLOT_IDX - target, attack_value))
                moves.extend(self.attack_cache.attack_moves())
                #moves.extend(self.attack_cache.load_cmd())
                #moves.append(self.attack_cache.cmd_terminator())
            else:
                self.attack_cache.invalidate()
                self.attack_cache.assign_registers()
                moves.extend(self.attack_cache.load_registers(strongest, MAX_SLOT_IDX - target, attack_value))
                moves.extend(self.attack_cache.attack_moves())
                #attack_moves = self.attack_cache.attack_moves()
                #moves.extend(attack_moves[:-1])
                #moves.extend(self.attack_cache.store_cmd())
                #moves.append(attack_moves[-1])
            return moves
        
        # Build vitality.
        src = self.get_vitality_src()
        vitality_transfer = self.player[src].vitality / 2
        
        if self.help_cache.is_valid():
            moves.extend(self.help_cache.load_registers(src, strongest, vitality_transfer))
            moves.extend(self.help_cache.help_moves())
        else:
            self.help_cache.invalidate()
            self.help_cache.assign_registers()
            moves.extend(self.help_cache.load_registers(src, strongest, vitality_transfer))
            moves.extend(self.help_cache.help_moves())
            
        #cmd_reg = self.get_register()
        #value_reg = self.get_register(cmd_reg + 1)
        #moves = self.cmd.set_integer(value_reg, vitality_transfer)
        #moves.extend(self.cmd.attack_slot(src, strongest, cmd_reg, value_reg))
        return moves
    
    def select_target(self):
        """ Return the index of the prefered target. """
        # The target is selected based on its stength and field contents.
        # Weaker targets with much content are selected first.
        slots = [(s.vitality - len(str(s.field)), ix) for ix, s in enumerate(self.opponent.slots) if s.alive]
        slots.sort()
        return slots[0][1]
    
    def get_vitality_src(self):
        slots = [(s.vitality, ix) for ix, s in enumerate(self.player.slots)]
        slots.sort()
        return slots[NBR_OF_SLOTS / 2][1]
