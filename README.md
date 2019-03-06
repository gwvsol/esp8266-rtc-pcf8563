## RTS PCF8563 работа с NTP и времеными зонами

[![micropython](https://user-images.githubusercontent.com/13176091/53680744-4dfcc080-3ce8-11e9-94e1-c7985181d6a5.png)](https://micropython.org/)

*PCF8563 имеет низкую точность работы, не смотря на использование в схеме кварцевого резонатора*

Функционал который имеет библиотека:
1. Обновление времени с NTP сервера (для этого используется библиотека [timezone](https://github.com/gwvsol/ESP8266-TimeZone))
2. Поддержка временных зон и перехода с летнего времени на зимнее

### Схема включения PCF8563

![schematic_esp8266-pcf8563-rtc](https://user-images.githubusercontent.com/13176091/53905720-ea5cf500-4051-11e9-9094-4fe478ee54e6.png)

Для работы с библиотекой:
```python
from machine import I2C, Pin
from i2c_pcf8563 import PCF8563
i2c = I2C(scl=Pin(14), sda=Pin(12), freq=400000)
rtc = PCF8563(i2c, 0x51, zone=3)
```
Вывод времени с pcf8563:
```python
rtc.datetime()
```
Запись нового значения времени
```python
rtc.datetime((19, 1, 13, 19, 0, 48, 6, 0))
```
Сброс времени до (2000, 1, 1, 0, 0, 0, 0, 0) это удобно использовать при отладке кода
```python
rtc.datetime('reset')
```

Обновление времени с NTP сервера
```python
rtc.settime('ntp')
```

Обновление времени с часов микроконтроллера
```python
rtc.settime('esp')
```

Обновление времени с летнего на зимнее и обратно
```python
rtc.settime('dht')
или
rtc.settime()
```

***Пример использования:***
```python
from machine import I2C, Pin
from i2c_pcf8563 import PCF8563
i2c = I2C(scl=Pin(14), sda=Pin(12), freq=400000)
rtc = PCF8563(i2c, 0x51, zone=3)
rtc.datetime()
(2000, 1, 1, 0, 9, 30, 5, 0)
rtc.settime('ntp')
#Get UTC time from NTP server...
#TIME ZONE Winter: 2
#RTC: Old Time: 2000-01-01 00:09:59
#RTC: New Time: 2019-01-24 12:47:19
```
```python
async def _dataupdate(self):
        while True:
            self.config['RTC_TIME'] = self.rtc.datetime()
            rtc = self.config['RTC_TIME']
            #Проверка летнего или зименего времени каждую минуту в 30с
            if rtc[5] == 30: 
                self.rtc.settime('dht')
            #Если у нас режим подключения к точке доступа и если есть соединение, подводим часы по NTP
            if self.config['MODE_WiFi'] == 'ST' and not self.config['no_wifi']:
                #Подводка часов по NTP каждые сутки в 22:00:00
                if rtc[3] == 22 and rtc[4] == 0 and rtc[5] < 3 and self.config['NTP_UPDATE']:
                        self.config['NTP_UPDATE'] = False
                        self.rtc.settime('ntp')
                        await asyncio.sleep(1)
                        self.config['NTP_UPDATE'] = True
            await asyncio.sleep(1)
```
