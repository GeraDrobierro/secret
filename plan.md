## 1 добавленная функция бота 
```python
import telebot
from telebot import types


bot = telebot.TeleBot(token='7175694691:AAGbBUhvNaKbC93_BSQynmzSeu5GCV_NAGo')


def main():
    @bot.message_handler(commands=['start'])  # декоратор, который получает значение ввиде команды \start
    def start(message):
        markup = types.ReplyKeyboardMarkup()  # создаю обьект на основе класса
        btn1 = types.KeyboardButton('/listen')  # основные кнопки бота
        btn2 = types.KeyboardButton('/add')
        btn3 = types.KeyboardButton('/view_all')
        btn4 = types.KeyboardButton('/options')
        markup.row(btn1, btn2, btn3, btn4)
        bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}, напиши /help', reply_markup=markup)
        # приветсвенное сообщение

if __name__ == '__main__':
    main()
    bot.polling()  # обращаюсь к методу обьекта bot, чтобы бот мог принимать сообщения и отправлять их

```

## 2 добавленная функция бота 
```python
@bot.message_handler(commands=['help'])  # Создал декоратор, который принимает в себя команду /help
    def help_info(message):
        markup = types.ReplyKeyboardMarkup()
        btn1 = types.KeyboardButton('/listen')  # Это основные кнопки бота
        btn2 = types.KeyboardButton('/add')
        btn3 = types.KeyboardButton('/view_all')
        btn4 = types.KeyboardButton('/options')
        markup.row(btn1, btn2, btn3, btn4)
        file = open('help.txt', 'r') 
        # Создаю переменную file и присваиваю ей файлиовый обьект с режимом доступа только для чтения
        k = file.read()  # переменной k передаем метод считывания данных из файла
        bot.send_message(message.chat.id, f'{k}', reply_markup=markup)  
        # бот отправляет сообщение с текстом и выводит кнопки на экран 
        file.close()  # закрываю файл
```
добавить её к функции 1 и создать help.txt на гитхабе.

## 3 добаленная функция 
```python
   @bot.message_handler(['add'])
    def song_name(message):
        conn = sqlite3.connect('music.sql')  # создаю обьект на основе класса sqlite3, т.е. создаю БД
        cur = conn.cursor()  # Создаю курсор для работы с БД

        cur.execute('CREATE TABLE IF NOT EXISTS loadings '
                    '(id int auto_increment primary key, name varchar(50), artist varchar(50))')
        # создаю таблицу с атрибутами name, artist и первичным ключом id
        conn.commit()  # обращаюсь к БД с нашим запросом
        cur.close()  # закрываю курсор
        conn.close()  # закрываю БД

        bot.send_message(message.chat.id, 'Введи название песни')
        bot.register_next_step_handler(message, naming)  # перенаправляю бота выполнить следующую функцию

    def naming(message):  # функция для 'регистрации' имени трека
        global name  # обьявляю переменную name как глобальную

        bot.send_message(message.chat.id, 'отправь аудио')
        name = message.text  # бот регистрирует название с сообщения пользователя

        bot.register_next_step_handler(message, save_audio)

    @bot.message_handler(content_types=['audio'])  # декоратор, который приниимает как значение аудиофайл
    def save_audio(message):  # функция сохранения аудиофайла в БД
        try:
            global name  # обьявляю переменную name, artist как глобальную
            global artist

            artist = message.audio.performer
            # обращаюсь к методу обьекта message, в котором хранится инф. о исполнителе

            audio_file_id = message.audio.file_id  # переменная, в которой храниться id сообщения
            audio_file = bot.get_file(audio_file_id)  # переменная, которая представляет собой полученный файл
            audio_file_path = audio_file.file_path

            audio_name = f"/ВАШ_ПУТЬ_К_ПАПКЕ_/MUSIC/{name}.mp3"

            audio_data = bot.download_file(audio_file_path)

            with open(audio_name, 'wb') as file:  # Открытие файла для записи в двоичном режиме
                file.write(audio_data)  # Запись данных аудиофайла в файл

            conn = sqlite3.connect('music.sql')
            cur = conn.cursor()

            cur.execute('INSERT INTO loadings (name, artist) VALUES ("%s", "%s")' % (name, artist))
            # Выполнение SQL-запроса для добавления информации об аудиофайле в БД
            conn.commit()
            cur.close()
            conn.close()

            markup = types.InlineKeyboardMarkup()
            bot.delete_message(message.chat.id, message.message_id)  # Удаление сообщения с аудиофайлом
            markup.add(types.InlineKeyboardButton('Весь плейлист', callback_data='loadings'))
            # Добавление кнопки к клавиатуре и вызываю функцию loadings
            bot.send_message(message.chat.id, 'Трек добавлен', reply_markup=markup)
        except AttributeError:  # обработка исключения, если сообщение не является аудиофайлом
            bot.send_message(message.chat.id, 'Друг, похоже ты отправил мне не аудиофайл. Отправь мне аудио, пожалуйста')

    @bot.callback_query_handler(func=lambda callback: True)  # Декоратор для обработки callback-запросов
    def callback_message(callback):  # Функция, которая будет вызываться при callback-запросах

        conn = sqlite3.connect('music.sql')
        cur = conn.cursor()

        cur.execute('SELECT * FROM loadings')
        loadings = cur.fetchall()

        info = ''   # Переменная для хранения информации о треках
        for i in loadings:
            info += f'Название трека:{i[1]}, Исполнитель: {i[2]}\n'  # Формирование строки информации о треке
        cur.close()
        conn.close()
        bot.send_message(callback.message.chat.id, info)  # Отправка сообщения с информацией о треках в чат

        
```

Блок кода идёт за предыдущим, здесь необходимо также обьявить переменные и импортировать библотеку sqlite3:

```python
import sqlite3  # Импортирую библиотеку для работы с БД

bot = telebot.TeleBot(token='7175694691:AAGbBUhvNaKbC93_BSQynmzSeu5GCV_NAGo')
name = None  # переменная, в которой будут храниться значения с названием аудиофайла
artist = None  # переменная, в которой будут храниться значения с названием артиста
```

## 4 добавленная функция 
```python
@bot.message_handler(commands=['view_all'])
    def view_all(message):  # функция для просморта всего плейлиста
        conn = sqlite3.connect('music.sql')
        cur = conn.cursor()

        cur.execute('SELECT * FROM loadings')
        loadings = cur.fetchall()

        info = ''
        for i in loadings:
            info += f'Название трека:{i[1]}, Исполнитель: {i[2]}\n'
        cur.close()
        conn.close()
        bot.send_message(message.chat.id, f'ВАШ ПЛЕЙЛИСТ: \n{info}')
```
## 5 добавленная функция 
```python
 @bot.message_handler(commands=['listen'])
    def listen(message):
        try:
            conn = sqlite3.connect('music.sql')  # обращаюсь к БД
            cur = conn.cursor()

            cur.execute('SELECT * FROM loadings')
            loadings = cur.fetchall()

            info = ''
            for i in loadings:
                info += f'Название трека:{i[1]}, Исполнитель: {i[2]}\n'
            cur.close()
            conn.close()
            bot.send_message(message.chat.id, f'ВАШ ПЛЕЙЛИСТ: \n{info}')  # иформация о плейлисте
            bot.register_next_step_handler(message, music_player)  # перенаправляю бота на выполнение следующей функци

        except sqlite3.OperationalError:  # обработка оишбок, если пользователь еще не загрузил трек
            bot.send_message(message.chat.id, 'Ты пока не загрузил песни')

    def music_player(message):
        conn = sqlite3.connect('music.sql')
        cur = conn.cursor()

        cur.execute('SELECT * FROM loadings')  # Выполнение SQL-запроса для выборки всех записей из таблицы loadings
        loadings = cur.fetchall()  # Получение результатов запроса
        checkout = message.text  # Получение текста сообщения
        for i in loadings:
            if checkout in f'{i[1]}':  # Проверяю, содержится ли текст сообщения в названии трека
                file = open(f'/ПУТЬ_К_ПАПКЕ_/MUSIC/{checkout}.mp3', 'rb')  
                # Открываю файл трека в двоичном режиме
                bot.send_audio(message.chat.id, file, title=f'{checkout}')  
                # Отправляю аудиофайла в чат с указанием заголовка
                file.close()
            else:
                pass
```
## 6 добавленная функция
```python
@bot.message_handler(commands=['options'])  # декоратор для обработки команды /options
    def song_name(message):
        markup = types.ReplyKeyboardMarkup()
        btn1 = types.KeyboardButton('/delete')
        btn2 = types.KeyboardButton('/edit')
        markup.row(btn1, btn2)
        bot.send_message(message.chat.id, 'Что вы хотите сделать ?', reply_markup=markup)
```

## 7 добавленная функция

```python
@bot.message_handler(commands=['delete'])
    def preparation_for_delete(message):
        bot.register_next_step_handler(message, delete)  # Регистрирую следующего обработчика для данного сообщения
        bot.send_message(message.chat.id, 'Введи название песни')
        conn = sqlite3.connect('music.sql')
        cur = conn.cursor()

        cur.execute('SELECT * FROM loadings')  # Выполняю SQL-запроса для выборки всех записей из таблицы loadings
        loadings = cur.fetchall()
        info = ''
        for i in loadings:
            info += f'Название трека: {i[1]}, Исполнитель: {i[2]}\n'  # Формирую строки с информацией о треках
        bot.send_message(message.chat.id, info)   # Отправляю информации о всех треках в чат

    def delete(message):

        markup = types.ReplyKeyboardMarkup()
        btn1 = types.KeyboardButton('/listen')
        btn2 = types.KeyboardButton('/add')
        btn3 = types.KeyboardButton('/view_all')
        btn4 = types.KeyboardButton('/options')
        markup.row(btn1, btn2, btn3, btn4)

        checkout = message.text  # Получаю названия трека для удаления
        conn = sqlite3.connect('music.sql')
        cur = conn.cursor()

        cur.execute('DELETE FROM loadings WHERE name = ?', (checkout,))
        # Удаляю записи с указанным названием из базы данных
        conn.commit()  # Сохраняю изменений

        file_path = os.path.join(f'/ПУТЬ_К_ПАПКЕ_/MUSIC/{checkout}.mp3')  # Путь к файлу трека
        try:
            os.remove(file_path)   # Попытка удалить файл трека
            print(f"Файл {checkout} успешно удален с сервера")
            bot.send_message(message.chat.id, 'Запись успешно удалена')

        except OSError as e:  # обрабатываю ошибку, если трека для удаления нет
            print(f"Ошибка удаления файла на сервере: {e}")
            bot.send_message(message.chat.id, 'Такого трека нет в твоём плейлисте, друг')

        cur.execute('SELECT * FROM loadings')
        loadings = cur.fetchall()
        info = ''
        for i in loadings:
            info += f'Название трека: {i[1]}, Исполнитель: {i[2]}\n'
        cur.close()
        conn.close()

        bot.send_message(message.chat.id, info, reply_markup=markup)

```

Импортируйте библиотеку os

```python
import os  # импортирую библиотеку для работы с сервером
```

## 8 добавленная функция

```python
@bot.message_handler(commands=['edit'])
    def find_old_name(message):

        bot.send_message(message.chat.id, 'Введи старое название песни')  # Запрос на ввод старого названия песни
        conn = sqlite3.connect('music.sql')
        cur = conn.cursor()

        cur.execute('SELECT * FROM loadings')
        loadings = cur.fetchall()
        info = ''
        for i in loadings:
            info += f'Название трека: {i[1]}, Исполнитель: {i[2]}\n'
        bot.send_message(message.chat.id, info)
        bot.register_next_step_handler(message, new_name)  # Регистрируем следующего обработчика для нового названия

    def new_name(message):
        global old_name   # Объявляем глобальную переменную для старого названия

        old_name = message.text   # Получаем старое название песни
        bot.send_message(message.chat.id, 'Введи новое название песни')  # Запрос на ввод нового названия песни
        bot.register_next_step_handler(message, edit)  # Регистрация следующего обработчика для изменения

    def edit(message):
        global old_name  # Объявление глобальной переменной для старого названия

        markup = types.ReplyKeyboardMarkup()
        btn1 = types.KeyboardButton('/listen')
        btn2 = types.KeyboardButton('/add')
        btn3 = types.KeyboardButton('/view_all')
        btn4 = types.KeyboardButton('/options')
        markup.row(btn1, btn2, btn3, btn4)

        checkout = old_name  # Присваиваем переменной старое название
        the_new_name = message.text   # Полученаем новое название песни

        conn = sqlite3.connect('music.sql')
        cur = conn.cursor()

        cur.execute("UPDATE loadings SET name = ? WHERE name = ?", (the_new_name, checkout))  # Обновление названия в БД
        conn.commit()

        file_path = f'/ПУТЬ_К_ПАПКЕ_/MUSIC/{checkout}.mp3'   # Путь к старому файлу
        new_file_path = f'/ПУТЬ_К_ПАПКЕ_/MUSIC/{the_new_name}.mp3'  # Путь к новому файлу

        try:
            os.rename(file_path, new_file_path)  # Переименование файла на сервере
            print(f"Файл {checkout} успешно обновлен на сервере")
            bot.send_message(message.chat.id, 'Запись успешно обновлена')
        except OSError as e:  # обработка ошибок, если трека для редактирования нет
            print(f"Ошибка обновления файла на сервере: {e}")
            bot.send_message(message.chat.id, 'Похоже такого трека нету в твоём плейлисте, друг')

        cur.execute('SELECT * FROM loadings')
        loadings = cur.fetchall()
        info = ''
        for i in loadings:
            info += f'Название трека: {i[1]}, Исполнитель: {i[2]}\n'

        cur.close()
        conn.close()

        bot.send_message(message.chat.id, info, reply_markup=markup)
```
Обьявите перменную в самом начале
```python
old_name = None
```

## 9 добавленная функция

```python
    @bot.message_handler()  # функция для обработки обычного текста
    def txt_random_validation(message):
        check = message.text
        if check != '/add' or '/start' or '/listen':  
            file = open('validation.txt', 'r')  # создаю файловый обьект для чтения
            k = file.read()
            bot.send_message(message.chat.id, f'{k}')  # отправляю информацию
            file.close()  # закрываю файл

```

Создать текстовый файл validation