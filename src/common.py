NBR_OF_SLOTS = 256
MAX_SLOT_IDX = NBR_OF_SLOTS - 1
DEFAULT_VITALITY = 10000
MAX_VITALITY = 65535
MAX_CALL_DEPTH = 1000
LEFT_APPLICATION = '1'
RIGHT_APPLICATION = '2'

class Error(Exception):
    def __init__(self, value):
        Exception.__init__(self, value)
        
class NoInteger(Error):
    def __init__(self, value):
        Error.__init__(self, value)
        
class NoFunction(Error):
    def __init__(self, value):
        Error.__init__(self, value)
        
class NoOpponent(Error):
    def __init__(self, value):
        Error.__init__(self, value)
        
class NotAlive(Error):
    def __init__(self, value):
        Error.__init__(self, value)
        
class NotDead(Error):
    def __init__(self, value):
        Error.__init__(self, value)
        
class WrongValue(Error):
    def __init__(self, value):
        Error.__init__(self, value)
        
class InvalidSlot(Error):
    def __init__(self, value):
        Error.__init__(self, value)
        
class CallDepthExceeded(Error):
    def __init__(self, value):
        Error.__init__(self, value)