from enum import Enum

class StreamQuality(Enum):
  LQ  = 1
  SD  = 2
  HD  = 3
  UHD = 4
  
class PlaylistType(Enum):
  KODIPVR = 1
  PLAIN   = 2
  NAMES   = 3
  JSON    = 4
  
class ItemType(Enum):
  STREAM    = 1
  PLAYLIST  = 2