# sensor-client

## Инструкция по установке
Библиотека работает для python>=3.8
1. ```python3 -m venv venv```
2. ```source venv/bin/activate```
3. ```python setup.py install```

## Использование
Теперь у себя в коде можем писать ```from sensor_client import Client``` и пользоваться библиотекой.

* `example.py` - Пример использования библиотеки
* `server.py` - Сервер который примерно моделирует поведение, которое описано в задаче. У него нет гарантии что он 100% работает правильно. Очень полезен при отладке и тестировании клиента.

Можно в отдельном окне терминала запустить `python server.py`. Сервер разворачивается локально и слушает 8765 порт.

И в отдельном окне запустить `python example.py`

## TODO
* Добавить логгирование
* Написать тесты
* Написать документацию
