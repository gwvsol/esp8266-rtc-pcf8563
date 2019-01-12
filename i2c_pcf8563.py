import machine
try:
    import utime as time
except:
    import time
#import uasyncio as asyncio
import gc
#from timezone import TZONE

class PCF8563(object):
    _CONTROL_1 = 0x00
    _CONTROL_2 = 0x01
    _SECONDS = 0x02
    _MINUTES = 0x03
    _HOURS = 0x04
    _DAY = 0x06
    _DATE = 0x05
    _MONTH = 0x07
    _YEAR = 0x08
    _CLK_OUT = 0x0D
    _ALARM_TIME = 0x09
    _ALARM_MINUTES = 0x09
    _ALARM_HOURS = 0x0A
    _ALARM_DAY = 0x0B
    _ALARM_WEEKDAY = 0x0B

    # Clock-out frequencies
    CLK_OUT_FREQ_32_DOT_768KHZ = 0x80
    CLK_OUT_FREQ_1_DOT_024KHZ = 0x81
    CLK_OUT_FREQ_32_KHZ = 0x82
    CLK_OUT_FREQ_1_HZ = 0x83
    CLK_HIGH_IMPEDANCE = 0x0
    
    #from machine import I2C, Pin
    #from i2c_pcf8563 import PCF8563
    #i2c = I2C(scl=Pin(14), sda=Pin(12), freq=400000)
    #rtc = PCF8563(i2c, 0x51)
    #def __init__(self, i2c, i2c_addr, zone=0, win=True, source_time='local'):
    def __init__(self, i2c, i2c_addr):
        self.i2c = i2c
        self.i2c_addr = i2c_addr
        self.timebuf = bytearray(7)
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
        return (((bcd & 0xf0) >> 4) * 10 + (bcd & 0x0f))

    # Преобразование в двоично-десятичный формат
    def _dec2bcd(self, dec):
        tens, units = divmod(dec, 10)
        return (tens << 4) + units

    def _tobytes(self, num):
        return num.to_bytes(1, 'little')

    #Записьь нового значения в PCF8563
    def _write(self, register, data):
        #print("addr =0x%x register = 0x%x data = 0x%x %i " % (self._addr, register, data,_bcd_to_int(data)))
        self.i2c.write_byte_data(self._addr, register, data)

    #Чтение из PCF8563
    def _read(self, data):
        returndata = self.i2c.read_byte_data(self._addr, data)
        #print("addr = 0x%x data = 0x%x %i returndata = 0x%x %i " % (self._addr, data, data, returndata, _bcd_to_int(returndata)))
        return returndata
        
    def _read_seconds(self):
        return _bcd_to_int(self._read(self._REG_SECONDS) & 0x7F)

    def _read_minutes(self):
        return _bcd_to_int(self._read(self._REG_MINUTES) & 0x7F)

    def _read_hours(self):
        d = self._read(self._REG_HOURS) & 0x3F
        return _bcd_to_int(d & 0x3F)

    def _read_day(self):
        return _bcd_to_int(self._read(self._REG_DAY) & 0x07)

    def _read_date(self):
        return _bcd_to_int(self._read(self._REG_DATE) & 0x3F)

    def _read_month(self):
        return _bcd_to_int(self._read(self._REG_MONTH) & 0x1F)

    def _read_year(self):
        return _bcd_to_int(self._read(self._REG_YEAR))

    def read_all(self):
        """Return a tuple such as (year, month, date, day, hours, minutes,
        seconds).
        """
        return (self._read_year(), self._read_month(), self._read_date(),
                self._read_day(), self._read_hours(), self._read_minutes(),
                self._read_seconds())

    def read_str(self):
        """Return a string such as 'YY-DD-MMTHH-MM-SS'.
        """
        return '%02d-%02d-%02dT%02d:%02d:%02d' % (self._read_year(),
                                                  self._read_month(), self._read_date(), self._read_hours(),
                                                  self._read_minutes(), self._read_seconds())
