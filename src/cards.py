import sys

from common import MAX_VITALITY, MAX_SLOT_IDX, MAX_CALL_DEPTH
from common import NoInteger, NoFunction, NoOpponent, NotAlive, NotDead, WrongValue, CallDepthExceeded

sys.setrecursionlimit(2 * MAX_CALL_DEPTH)

def card(name):
    """ Return an instance of the card with the given name. """
    cls = CARDS[name]
    return cls()
    
class Card(object):
    def __init__(self):
        pass
        
    def __str__(self):
        return self.name
    
    @property
    def name(self):
        return self.__class__.__name__
    
class Function(Card):
    # Total call count.
    calls = 0
    
    def __init__(self):
        Card.__init__(self)
        
    def __call__(self):
        Function.calls += 1
        if Function.calls > MAX_CALL_DEPTH:
            raise CallDepthExceeded("Call depth exceeded when calling function '%s'." % self.name)
    
    def __int__(self):
        raise NoInteger("Cards of type '%s' has no integer value." % self.name)
        
class I(Function):
    def __init__(self):
        Function.__init__(self)
    
    def __call__(self, state, x):
        Function.__call__(self)
        return x
        
class zero(Card):
    def __init__(self):
        Card.__init__(self)
    
    def __call__(self, state, x):
        raise NoFunction("Cards of type 'zero' are not callable.")
    
    def __int__(self):
        return 0
    
class succ(Function):
    def __init__(self):
        Function.__init__(self)
    
    def __call__(self, state, n):
        Function.__call__(self)
        m = int(n) + 1
        if m > MAX_VITALITY:
            m = MAX_VITALITY
        return m
            
class dbl(Function):
    def __init__(self):
        Function.__init__(self)
    
    def __call__(self, state, n):
        Function.__call__(self)
        m = 2 * int(n)
        if m > MAX_VITALITY:
            m = MAX_VITALITY
        return m
           
class get(Function):
    def __init__(self):
        Function.__init__(self)
    
    def __call__(self, state, i):
        Function.__call__(self)
        slot = state[int(i)]
        if slot.alive:
            return slot.field
        else:
            raise NotAlive("Slot %d is not alive, 'get' failed.")

class put(Function):
    def __init__(self):
        Function.__init__(self)
    
    def __call__(self, state, x):
        Function.__call__(self)
        return I()
        
class S(Function):
    def __init__(self):
        Function.__init__(self)
        self.f = None
        self.g = None
    
    def __call__(self, state, x):
        Function.__call__(self)
        if self.f is None:
            self.f = x
            return self
        elif self.g is None:
            self.g = x
            return self
        else:
            h = self.f(state, x)
            y = self.g(state, x)
            z = h(state, y)
            return z
    
    def __str__(self):
        if self.f is None:
            return 'S'
        elif self.g is None:
            return 'S(%s)' % self.f
        else:
            return 'S(%s)(%s)' % (self.f, self.g)
        
class K(Function):
    def __init__(self):
        Function.__init__(self)
        self.x = None
    
    def __call__(self, state, x):
        Function.__call__(self)
        if self.x is None:
            self.x = x
            return self
        else:
            return self.x
    
    def __str__(self):
        if self.x is None:
            return 'K'
        else:
            return 'K(%s)' % self.x
        
class inc(Function):
    def __init__(self):
        Function.__init__(self)
    
    def __call__(self, state, i):
        Function.__call__(self)
        slot = state[int(i)]
        if slot.alive:
            slot.vitality += 1
            if slot.vitality > MAX_VITALITY:
                slot.vitality = MAX_VITALITY
        return I()
        
class dec(Function):
    def __init__(self):
        Function.__init__(self)
    
    def __call__(self, state, i):
        Function.__call__(self)
        if state.opponent is not None:
            slot = state.opponent[int(MAX_SLOT_IDX - i)]
            if slot.alive:
                slot.vitality -= 1
        return I()
            
class attack(Function):
    def __init__(self):
        Function.__init__(self)
        self.i = None
        self.j = None
    
    def __call__(self, state, x):
        Function.__call__(self)
        if self.i is None:
            # x -> i
            self.i = x
            return self
        elif self.j is None:
            # x -> j
            self.j = x
            return self
        else:
            # x -> n
            n = int(x)
            slot = state[int(self.i)]
            # n must not be greater than v[i]
            if n > slot.vitality:
                raise WrongValue("n > v[i] (n=%d, v[%d]=%d), 'attack' failed." % (n, i, slot.vitality))
            slot.vitality -= n
            if state.opponent is not None:
                slot = state.opponent[MAX_SLOT_IDX - int(self.j)]
                # Do nothing if the slot is dead.
                if slot.alive:
                    slot.vitality -= 9 * n / 10
                    # Vitality can't decrease below zero.
                    if slot.vitality < 0:
                        slot.vitality = 0
            return I()
    
    def __str__(self):
        if self.i is None:
            return 'attack'
        elif self.j is None:
            return 'attack(%s)' % self.i
        else:
            return 'attack(%s)(%s)' % (self.i, self.j)
        
class help(Function):
    def __init__(self):
        Function.__init__(self)
        self.i = None
        self.j = None
    
    def __call__(self, state, x):
        Function.__call__(self)
        if self.i is None:
            # x -> i
            self.i = x
            return self
        elif self.j is None:
            # x -> j
            self.j = x
            return self
        else:
            # x -> n
            n = int(x)
            slot = state[int(self.i)]
            # n must not be greater than v[i]
            if n > slot.vitality:
                raise WrongValue("n > v[i] (n=%d, v[%d]=%d), 'help' failed." % (n, i, slot.vitality))
            slot.vitality -= n
            slot = state[int(self.j)]
            # Do nothing if the slot is dead.
            if slot.alive:
                slot.vitality += n * 11 / 10
                if slot.vitality > MAX_VITALITY:
                    slot.vitality = MAX_VITALITY
            return I()
    
    def __str__(self):
        if self.i is None:
            return 'help'
        elif self.j is None:
            return 'help(%s)' % self.i
        else:
            return 'help(%s)(%s)' % (self.i, self.j)
    
class copy(Function):
    def __init__(self):
        Function.__init__(self)
    
    def __call__(self, state, i):
        Function.__call__(self)
        if state.opponent is None:
            raise NoOpponent("The 'copy' card was called in single player mode.")
        slot = state.opponent[int(i)]
        return slot.field
    
class revive(Function):
    def __init__(self):
        Function.__init__(self)
    
    def __call__(self, state, i):
        Function.__call__(self)
        slot = state[int(i)]
        if not slot.alive:
            slot.vitality = 1
        return I()
        
class zombie(Function):
    def __init__(self):
        Function.__init__(self)
        self.i = None
    
    def __call__(self, state, x):
        Function.__call__(self)
        if self.i is None:
            self.i = x
            return self
        else:
            if state.opponent is not None:
                slot = state.opponent[MAX_SLOT_IDX - int(self.i)]
                if slot.alive:
                    raise NotDead("Function 'zombie' applied to a slot that is alive.")
                slot.field = x
                slot.vitality = -1
            return I()
    
    def __str__(self):
        if self.i is None:
            return 'zombie'
        else:
            return 'zombie(%s)' % self.i
        
CARDS = dict([(c.__name__, c) for c in [I, zero, succ, dbl, get, put, S, K, inc, dec, attack, help, copy, revive, zombie]])