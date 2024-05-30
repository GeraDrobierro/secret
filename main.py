import config
import telebot
import sqlite3
from telebot import types
import os


bot = telebot.TeleBot(config.token)
name = None
artist = None
old_name = None


def main():
    @bot.message_handler(commands=['help'])
    def start(message):
        markup = types.ReplyKeyboardMarkup()
        btn1 = types.KeyboardButton('/listen')
        btn2 = types.KeyboardButton('/add')
        btn3 = types.KeyboardButton('/view_all')
        btn4 = types.KeyboardButton('/options')
        markup.row(btn1, btn2, btn3, btn4)
        file = open('help.txt', 'r')
        k = file.read()
        bot.send_message(message.chat.id, f'{k}', reply_markup=markup)
        file.close()

    @bot.message_handler(commands=['start'])
    def start(message):
        markup = types.ReplyKeyboardMarkup()
        btn1 = types.KeyboardButton('/listen')
        btn2 = types.KeyboardButton('/add')
        btn3 = types.KeyboardButton('/view_all')
        btn4 = types.KeyboardButton('/options')
        markup.row(btn1, btn2, btn3, btn4)
        bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}, напиши /help', reply_markup=markup)

    @bot.message_handler(commands=['listen'])
    def listen(message):
        try:
            conn = sqlite3.connect('music.sql')
            cur = conn.cursor()

            cur.execute('SELECT * FROM loadings')
            loadings = cur.fetchall()

            info = ''
            for i in loadings:
                info += f'Название трека:{i[1]}, Исполнитель: {i[2]}\n'
            cur.close()
            conn.close()
            bot.send_message(message.chat.id, 'ВАШ ПЛЕЙЛИСТ:')
            bot.send_message(message.chat.id, info)
            bot.register_next_step_handler(message, music_player)

        except sqlite3.OperationalError:
            bot.send_message(message.chat.id, 'Ты пока не загрузил песни')

    def music_player(message):
        conn = sqlite3.connect('music.sql')
        cur = conn.cursor()

        cur.execute('SELECT * FROM loadings')
        loadings = cur.fetchall()
        checkout = message.text
        for i in loadings:
            if checkout in f'{i[1]}':
                file = open(f'/Users/david/pythonProject274/MUSIC/{checkout}.mp3', 'rb')
                bot.send_audio(message.chat.id, file, title=f'{checkout}')
                file.close()
            else:
                pass

    @bot.message_handler(commands=['view_all'])
    def view_all(message):
        conn = sqlite3.connect('music.sql')
        cur = conn.cursor()

        cur.execute('SELECT * FROM loadings')
        loadings = cur.fetchall()

        info = ''
        for i in loadings:
            info += f'Название трека:{i[1]}, Исполнитель: {i[2]}\n'
        cur.close()
        conn.close()
        bot.send_message(message.chat.id, info)

    @bot.callback_query_handler(func=lambda callback: True)
    def callback_message(callback):

        conn = sqlite3.connect('music.sql')
        cur = conn.cursor()

        cur.execute('SELECT * FROM loadings')
        loadings = cur.fetchall()

        info = ''
        for i in loadings:
            info += f'Название трека:{i[1]}, Исполнитель: {i[2]}\n'
        cur.close()
        conn.close()
        bot.send_message(callback.message.chat.id, info)

    @bot.message_handler(['add'])
    def song_name(message):
        conn = sqlite3.connect('music.sql')
        cur = conn.cursor()

        cur.execute('CREATE TABLE IF NOT EXISTS loadings (id int auto_increment primary key, name varchar(50), artist varchar(50))')
        conn.commit()
        cur.close()
        conn.close()

        bot.send_message(message.chat.id, 'Введи название песни')
        bot.register_next_step_handler(message, naming)

    def naming(message):
        global name

        bot.send_message(message.chat.id, 'отправь аудио')
        name = message.text

        bot.register_next_step_handler(message, save_audio)

    @bot.message_handler(content_types=['audio'])
    def save_audio(message):
        global name
        global artist

        artist = message.audio.performer

        audio_file_id = message.audio.file_id
        audio_file = bot.get_file(audio_file_id)
        audio_file_path = audio_file.file_path

        audio_name = f"/Users/david/pythonProject274/MUSIC/{name}.mp3"

        audio_data = bot.download_file(audio_file_path)

        with open(audio_name, 'wb') as file:
            file.write(audio_data)
        print(audio_data)

        conn = sqlite3.connect('music.sql')
        cur = conn.cursor()

        cur.execute('INSERT INTO loadings (name, artist) VALUES ("%s", "%s")' % (name, artist))
        conn.commit()
        cur.close()
        conn.close()

        markup = types.InlineKeyboardMarkup()
        bot.delete_message(message.chat.id, message.message_id)
        markup.add(types.InlineKeyboardButton('Весь плейлист', callback_data='loadings'))
        bot.send_message(message.chat.id, 'Трек добавлен', reply_markup=markup)

    @bot.message_handler(commands=['options'])
    def song_name(message):

        markup = types.ReplyKeyboardMarkup()
        btn1 = types.KeyboardButton('/delete')
        btn2 = types.KeyboardButton('/edit')
        markup.row(btn1, btn2)
        bot.send_message(message.chat.id, 'Что вы хотите сделать ?', reply_markup=markup)

    @bot.message_handler(commands=['delete'])
    def preparation_for_delete(message):
        bot.register_next_step_handler(message, delete)
        bot.send_message(message.chat.id, 'Введи название песни')
        conn = sqlite3.connect('music.sql')
        cur = conn.cursor()

        cur.execute('SELECT * FROM loadings')
        loadings = cur.fetchall()
        info = ''
        for i in loadings:
            info += f'Название трека: {i[1]}, Исполнитель: {i[2]}\n'
        bot.send_message(message.chat.id, info)

    def delete(message):

        markup = types.ReplyKeyboardMarkup()
        btn1 = types.KeyboardButton('/listen')
        btn2 = types.KeyboardButton('/add')
        btn3 = types.KeyboardButton('/view_all')
        btn4 = types.KeyboardButton('/options')
        markup.row(btn1, btn2, btn3, btn4)

        checkout = message.text
        conn = sqlite3.connect('music.sql')
        cur = conn.cursor()

        cur.execute('DELETE FROM loadings WHERE name = ?', (checkout,))
        conn.commit()

        file_path = os.path.join(f'/Users/david/pythonProject274/MUSIC/{checkout}.mp3')
        try:
            os.remove(file_path)
            print(f"Файл {checkout} успешно удален с сервера")
            bot.send_message(message.chat.id, 'Запись успешно удалена')

        except OSError as e:
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

    @bot.message_handler(commands=['edit'])
    def find_old_name(message):

        bot.send_message(message.chat.id, 'Введи старое название песни')
        conn = sqlite3.connect('music.sql')
        cur = conn.cursor()

        cur.execute('SELECT * FROM loadings')
        loadings = cur.fetchall()
        info = ''
        for i in loadings:
            info += f'Название трека: {i[1]}, Исполнитель: {i[2]}\n'
        bot.send_message(message.chat.id, info)
        bot.register_next_step_handler(message, new_name)

    def new_name(message):
        global old_name

        old_name = message.text
        bot.send_message(message.chat.id, 'Введи новое название песни')
        bot.register_next_step_handler(message, edit)

    def edit(message):
        global old_name

        markup = types.ReplyKeyboardMarkup()
        btn1 = types.KeyboardButton('/listen')
        btn2 = types.KeyboardButton('/add')
        btn3 = types.KeyboardButton('/view_all')
        btn4 = types.KeyboardButton('/options')
        markup.row(btn1, btn2, btn3, btn4)

        checkout = old_name
        the_new_name = message.text

        conn = sqlite3.connect('music.sql')
        cur = conn.cursor()

        cur.execute("UPDATE loadings SET name = ? WHERE name = ?", (the_new_name, checkout))
        conn.commit()

        file_path = f'/Users/david/pythonProject274/MUSIC/{checkout}.mp3'
        new_file_path = f'/Users/david/pythonProject274/MUSIC/{the_new_name}.mp3'

        try:
            os.rename(file_path, new_file_path)
            print(f"Файл {checkout} успешно обновлен на сервере")
            bot.send_message(message.chat.id, 'Запись успешно обновлена')
        except OSError as e:
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

    @bot.message_handler()
    def txt_random_validation(message):
        check = message.text
        if check != '/add' or '/start' or '/listen':
            file = open('validation.txt', 'r')
            k = file.read()
            bot.send_message(message.chat.id, f'{k}')
            file.close()

    bot.polling()

if __name__ == '__main__':
    main()
