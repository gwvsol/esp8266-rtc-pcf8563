import machine
try:
    import utime as time
except:
    import time
import uasyncio as asyncio
import gc
from timezone import TZONE

class PCF8563(object):
