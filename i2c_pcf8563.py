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
_DATE = 0x05
_WDAY = 0x06
_MONTH = 0x07
_YEAR = 0x08

class PCF8563(object):
    #def __init__(self, i2c, i2c_addr, zone=0, dht=True, source_time='local'):
    def __init__(self, i2c, i2c_addr):
        self.i2c = i2c
        self.i2c_addr = i2c_addr
        self.timebuf = None
        #self.zone = zone
        #self.win = dht
        #self.stime = source_time
        #self.tzone = TZONE(self.zone)
        #self.rtc = False # Изменяется на True только когда март или октябрь и только в последнее воскресенье месяца
        if self.i2c_addr in self.i2c.scan():
            print('RTS PCF8563 find at address: 0x%x ' %(self.i2c_addr))
        else:
            print('RTS PCF8563 not found at address: 0x%x ' %(self.i2c_addr))
        gc.collect() #Очищаем RAM

    #Преобразование двоично-десятичного формата
    def _bcd2dec(self, bcd):
        """Convert binary coded decimal (BCD) format to decimal"""
        return (((bcd & 0xf0) >> 4) * 10 + (bcd & 0x0f))

    #Преобразование в двоично-десятичный формат
    def _dec2bcd(self, dec):
        """Convert decimal to binary coded decimal (BCD) format"""
        tens, units = divmod(dec, 10)
        return (tens << 4) + units

    def _tobytes(self, num):
        return num.to_bytes(1, 'little')

    #Чтение времени или запись нового знвчения и преобразование в формат ESP8266
    #Возвращает кортеж в формате localtime() (в ESP8266 0 - понедельник, а 6 - воскресенье)
    def datetime(self, datetime=None):
        """Reading RTC time and convert to ESP8266 and Direct write un-none value.
        Range: seconds [0,59], minutes [0,59], hours [0,23],
        day [0,7], date [1-31], month [1-12], year [0-99]."""
        if datetime == None:
            """Reading RTC time and convert to ESP8266"""
            data = self.i2c.readfrom_mem(self.i2c_addr, _SECONDS, 7)
            ss = self._bcd2dec(data[0] & 0x7F)
            mm = self._bcd2dec(data[1] & 0x7F)
            hh = self._bcd2dec(data[2] & 0x3F)
            dd = self._bcd2dec(data[3] & 0x3F)
            wday = data[4] & 0x07
            MM = self._bcd2dec(data[5] & 0x1F)
            yy = self._bcd2dec(data[6]) + 2000
            return yy, MM, dd, hh, mm, ss, wday, 0 # wday in esp8266 0 == Monday, 6 == Sunday
        elif datetime != None:
            """Direct write un-none value"""
            if datetime == 'reset':
                (yy, MM, mday, hh, mm, ss, wday, yday) = (0, 1, 1, 0, 0, 0, 0, 0)
            else:
                (yy, MM, mday, hh, mm, ss, wday, yday) = datetime
            if ss < 0 or ss > 59:
                raise ValueError('Seconds is out of range [0,59].')
            self.i2c.writeto_mem(self.i2c_addr, _SECONDS, self._tobytes(self._dec2bcd(ss)))
            if mm < 0 or mm > 59:
                raise ValueError('Minutes is out of range [0,59].')
            self.i2c.writeto_mem(self.i2c_addr, _MINUTES, self._tobytes(self._dec2bcd(mm)))
            if hh < 0 or hh > 23:
                raise ValueError('Hours is out of range [0,23].')
            self.i2c.writeto_mem(self.i2c_addr, _HOURS, self._tobytes(self._dec2bcd(hh)))  #Sets to 24hr mode
            if mday < 1 or mday > 31:
                raise ValueError('Date is out of range [1,31].')
            self.i2c.writeto_mem(self.i2c_addr, _DATE, self._tobytes(self._dec2bcd(mday)))  #Day of month
            if wday < 0 or wday > 6:
                raise ValueError('Day is out of range [0,6].')
            self.i2c.writeto_mem(self.i2c_addr, _WDAY, self._tobytes(self._dec2bcd(wday)))
            if MM < 1 or MM > 12:
                raise ValueError('Month is out of range [1,12].')
            self.i2c.writeto_mem(self.i2c_addr, _MONTH, self._tobytes(self._dec2bcd(MM)))
            if yy < 0 or yy > 99:
                raise ValueError('Years is out of range [0,99].')
            self.i2c.writeto_mem(self.i2c_addr, _YEAR, self._tobytes(self._dec2bcd(yy)))
            (yy, MM, mday, hh, mm, ss, wday, yday) = self.datetime()
            print('New RTC Time: %02d-%02d-%02d %02d:%02d:%02d' %(yy, MM, mday, hh, mm, ss)) #Выводим новое время PCF8563


