#import machine
try:
    import utime as time
except:
    import time
#import uasyncio as asyncio
import gc
#from timezone import TZONE

#Registers overview
_SECONDS = 0x02
_MINUTES = 0x03
_HOURS = 0x04
_DAY = 0x06
_DATE = 0x05
_MONTH = 0x07
_YEAR = 0x08

    # Clock-out frequencies
#    CLK_OUT_FREQ_32_DOT_768KHZ = 0x80
#    CLK_OUT_FREQ_1_DOT_024KHZ = 0x81
#    CLK_OUT_FREQ_32_KHZ = 0x82
#    CLK_OUT_FREQ_1_HZ = 0x83
#    CLK_HIGH_IMPEDANCE = 0x0

class PCF8563(object):
    #def __init__(self, i2c, i2c_addr, zone=0, win=True, source_time='local'):
    def __init__(self, i2c, i2c_addr):
        self.i2c = i2c
        self.i2c_addr = i2c_addr
        self.timebuf = None
        #self.zone = zone
        #self.win = win
        #self.stime = source_time
        #self.tzone = TZONE(self.zone)
        #self.rtc = False # Изменяется на True только когда март или октябрь и только в последнее воскресенье месяца
        if self.i2c_addr in self.i2c.scan():
            print('RTS PCF8563 find at address: 0x%x ' %(self.i2c_addr))
        else:
            print('RTS PCF8563 not found at address: 0x%x ' %(self.i2c_addr))
        gc.collect() #Очищаем RAM


    # Преобразование двоично-десятичного формата
    def _bcd2dec(self, bcd):
        """Convert binary coded decimal (BCD) format to decimal"""
        return (((bcd & 0xf0) >> 4) * 10 + (bcd & 0x0f))

    # Преобразование в двоично-десятичный формат
    def _dec2bcd(self, dec):
        """Convert decimal to binary coded decimal (BCD) format"""
        tens, units = divmod(dec, 10)
        return (tens << 4) + units

    # Чтение из PCF8563
    def read_time(self):
        """Reading RTC time"""
        self.timebuf = self.i2c.readfrom_mem(self.i2c_addr, _SECONDS, 7)
        return self._convert()
        
#    def _write(self):
#        """Record the time value in the RTC clock"""
#        self.i2c.writeto_mem(self.i2c_addr, DATETIME_REG, 7)

    # Преобразуем время RTC PCF8563 в формат ESP8266
    # Возвращает кортеж в формате localtime() (в ESP8266 0 - понедельник, а 6 - воскресенье)
    def _convert(self):
        """Time convert to ESP8266"""
        data = self.timebuf
        ss = self._bcd2dec(data[0] & 0x7F)
        mm = self._bcd2dec(data[1] & 0x7F)
        hh = self._bcd2dec(data[2] & 0x3F)
        dd = self._bcd2dec(data[3] & 0x3F)
        wday = data[4] & 0x07
        MM = self._bcd2dec(data[5] & 0x1F)
        yy = self._bcd2dec(data[6]) + 2000
        # Time from PCF8563 in time.localtime() format (less yday)
        result = yy, MM, dd, hh, mm, ss, wday, 0 # wday in esp8266 0 == Monday, 6 == Sunday
        return result
        
#    #(YY, MM, mday, hh, mm, ss, wday, yday) = (2000, 1, 1, 0, 0, 0, 0, 0)
#   def save_time(self, dtime=(2000, 1, 1, 0, 0, 0, 0, 0)):
#        """Direct write un-none value.
#        Range: seconds [0,59], minutes [0,59], hours [0,23],
#               day [0,7], date [1-31], month [1-12], year [0-99].
#        """
#        if dtime[5] < 0 or dtime[5] > 59:
#            raise ValueError('Seconds is out of range [0,59].')
