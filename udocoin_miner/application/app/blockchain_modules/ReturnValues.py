from enum import Enum

class ReturnValues(Enum):
    SingleBlockRejected = 0 
    SingleBlockAppended = 1
    BlocksRejected = 2
    BlocksReplaced = 3