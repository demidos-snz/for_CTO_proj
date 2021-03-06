# for_CTO_proj
- **Умный сервис прогноза погоды, базовый уровень сложности.**
- **Проектирование сервиса:**
    - Язык программирования: Python 3.7, aiogram - asynchronous framework for Telegram Bot API;
    - Пользовательский интерфейс: Telegram-бот;
    - Формат ответа:
    
        **Данные об описании погоды, температуре, давлении и скорости ветра и дате прогноза, 
        полученные с API подставляются в текстовый шаблон**
         
            Температура: ___
            Давление: ___
            Скорость ветра: ___
            Дата: ___
            
        **и отправляются пользователю.**

- **Работа сервиса:**
    https://yadi.sk/i/cvumj82winyxxw
- **Распишите по шагам весь процесс работы программы.**

    **Сервис - Telegram-бот в роли FAQ, который по заданному городу пользователя, высылает ему ответ**

    Данные приходят от пользователя через интерфейс мессенджера

     → для начала работы бота нужно выполнить команду /start или /help;
     
     → формируется и отправляется запрос к API прогноза погоды;
     
     → если город существует, то заносим его в таблицу towns;  

     → формируется и отправляется ответ пользователю;
     
     → выбранный город можно добавить в список любимых (не более 5);
     
     → любимые города заносятся в таблицу users_favourite_towns, если город есть в таблице, то он не заносится;
     
     → команда /rm удаляет очищает список любимых городов из БД и панели пользователя.
     
- **Запуск программы:**
    - git clone https://github.com/demidos-snz/for_CTO_proj.git
    - cd ./for_CTO_proj
    - python -m venv ./venv
    - cd ./venv/Scripts/
    - activate
    - cd ../..
    - pip install -r requirements.txt
    - python ./main.py