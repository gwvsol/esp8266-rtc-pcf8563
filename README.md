## ПИД контроллер для ESP8266


За основу данной библиотеки была взят [simple-pid](https://github.com/m-lundberg/simple-pid/blob/master/README.md#simple-pid).

Указанная выше библиотека была адаптирована для работы с микроконтроллерами ESP8266
В основе этой библиотеки лежит руководство [Brett Beauregards](http://brettbeauregard.com/blog/2011/04/improving-the-beginners-pid-introduction/).

[Документация](https://simple-pid.readthedocs.io/en/latest/simple_pid.html#module-simple_pid.PID) для ПИД контроллера

***Пример использования:***
```python
from esp_pid import PID
pid = PID(1, 0.1, 0.05, setpoint=1)

# у нас есть система которую хотим контролировать
v = controlled_system.update(0)

while True:
    # расчет погрешности ПИД контроллером
    control = pid(v)
    
    # применение к контролируемой системе расчитанной ПИД контроллером новой погрешности
    v = controlled_system.update(control)
```
