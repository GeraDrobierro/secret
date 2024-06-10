import telebot
import sqlite3
from telebot import types
import os


bot = telebot.TeleBot(token='7175694691:AAGbBUhvNaKbC93_BSQynmzSeu5GCV_NAGo')
name = None
artist = None
old_name = None


def main():
    def get_playlist_info():
        conn = sqlite3.connect('music.sql')
        cur = conn.cursor()
        cur.execute('SELECT * FROM loadings')
        loadings = cur.fetchall()
        cur.close()
        conn.close()
        info = '\n'.join(f'Название трека: {i[1]}, Исполнитель: {i[2]}' for i in loadings)
        return info

    def create_main_markup():
        markup = types.ReplyKeyboardMarkup()
        btn_list = ['/listen', '/add', '/view_all', '/options']
        for btn in btn_list:
            markup.row(types.KeyboardButton(btn))
        return markup

    def send_playlist(message):
        info = get_playlist_info()
        bot.send_message(message.chat.id, 'ВАШ ПЛЕЙЛИСТ:')
        bot.send_message(message.chat.id, info)

    def start_message(message, text):
        bot.send_message(message.chat.id, text, reply_markup=create_main_markup())

    @bot.message_handler(commands=['help'])
    def help_message(message):
        with open('help.txt', 'r') as file:
            k = file.read()
        start_message(message, k)

    @bot.message_handler(commands=['start'])
    def start(message):
        start_message(message, f'Привет, {message.from_user.first_name}, напиши /help')

    @bot.message_handler(commands=['listen'])
    def listen(message):
        try:
            send_playlist(message)
            bot.register_next_step_handler(message, music_player)
        except sqlite3.OperationalError:
            bot.send_message(message.chat.id, 'Ты пока не загрузил песни')

    def music_player(message):
        conn = sqlite3.connect('music.sql')
        cur = conn.cursor()
        checkout = message.text
        cur.execute('SELECT * FROM loadings WHERE name=?', (checkout,))
        track = cur.fetchone()
        cur.close()
        conn.close()
        if track:
            file_path = f'/Users/david/pythonProject274/MUSIC/{checkout}.mp3'
            with open(file_path, 'rb') as file:
                bot.send_audio(message.chat.id, file, title=f'{checkout}')

    @bot.message_handler(commands=['view_all'])
    def view_all(message):
        bot.send_message(message.chat.id, get_playlist_info())

    @bot.callback_query_handler(func=lambda callback: True)
    def callback_message(callback):
        bot.send_message(callback.message.chat.id, get_playlist_info())

    @bot.message_handler(commands=['add'])
    def song_name(message):
        conn = sqlite3.connect('music.sql')
        cur = conn.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS loadings (id INTEGER PRIMARY KEY, name TEXT, artist TEXT)')
        conn.commit()
        cur.close()
        conn.close()
        bot.send_message(message.chat.id, 'Введи название песни')
        bot.register_next_step_handler(message, naming)

    def naming(message):
        global name
        name = message.text
        bot.send_message(message.chat.id, 'отправь аудио')
        bot.register_next_step_handler(message, save_audio)

    @bot.message_handler(content_types=['audio'])
    def save_audio(message):
        try:
            global name, artist
            artist = message.audio.performer
            audio_name = f"/Users/david/pythonProject274/MUSIC/{name}.mp3"
            audio_data = bot.download_file(bot.get_file(message.audio.file_id).file_path)

            with open(audio_name, 'wb') as file:
                file.write(audio_data)

            conn = sqlite3.connect('music.sql')
            cur = conn.cursor()
            cur.execute('INSERT INTO loadings (name, artist) VALUES (?, ?)', (name, artist))
            conn.commit()
            cur.close()
            conn.close()

            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('Весь плейлист', callback_data='loadings'))
            bot.delete_message(message.chat.id, message.message_id)
            bot.send_message(message.chat.id, 'Трек добавлен', reply_markup=markup)
        except AttributeError:
            bot.send_message(message.chat.id, 'Друг, похоже ты отправил мне не аудиофайл. Отправь мне аудио, пожалуйста')

    @bot.message_handler(commands=['options'])
    def options_message(message):
        markup = types.ReplyKeyboardMarkup()
        btn_list = ['/delete', '/edit']
        for btn in btn_list:
            markup.row(types.KeyboardButton(btn))
        bot.send_message(message.chat.id, 'Что вы хотите сделать?', reply_markup=markup)

    @bot.message_handler(commands=['delete'])
    def preparation_for_delete(message):
        bot.send_message(message.chat.id, 'Введи название песни')
        bot.send_message(message.chat.id, get_playlist_info())
        bot.register_next_step_handler(message, delete)

    def delete(message):
        track_name = message.text
        conn = sqlite3.connect('music.sql')
        cur = conn.cursor()
        cur.execute('DELETE FROM loadings WHERE name = ?', (track_name,))
        conn.commit()
        cur.close()
        conn.close()

        file_path = f'/Users/david/pythonProject274/MUSIC/{track_name}.mp3'
        try:
            os.remove(file_path)
            bot.send_message(message.chat.id, 'Запись успешно удалена')
        except OSError:
            bot.send_message(message.chat.id, 'Такого трека нет в твоём плейлисте, друг')
        bot.send_message(message.chat.id, get_playlist_info(), reply_markup=create_main_markup())

    @bot.message_handler(commands=['edit'])
    def find_old_name(message):
        bot.send_message(message.chat.id, 'Введи старое название песни')
        bot.send_message(message.chat.id, get_playlist_info())
        bot.register_next_step_handler(message, new_name)

    def new_name(message):
        global old_name
        old_name = message.text
        bot.send_message(message.chat.id, 'Введи новое название песни')
        bot.register_next_step_handler(message, edit)

    def edit(message):
        global old_name
        the_new_name = message.text
        conn = sqlite3.connect('music.sql')
        cur = conn.cursor()
        cur.execute("UPDATE loadings SET name = ? WHERE name = ?", (the_new_name, old_name))
        conn.commit()
        cur.close()
        conn.close()

        old_file_path = f'/Users/david/pythonProject274/MUSIC/{old_name}.mp3'
        new_file_path = f'/Users/david/pythonProject274/MUSIC/{the_new_name}.mp3'
        try:
            os.rename(old_file_path, new_file_path)
            bot.send_message(message.chat.id, 'Запись успешно обновлена')
        except OSError:
            bot.send_message(message.chat.id, 'Похоже такого трека нет в твоём плейлисте, друг')
        bot.send_message(message.chat.id, get_playlist_info(), reply_markup=create_main_markup())

    @bot.message_handler()
    def txt_random_validation(message):
        check = message.text
        if check not in ['/add', '/start', '/listen']:
            with open('validation.txt', 'r') as file:
                k = file.read()
            bot.send_message(message.chat.id, k)

    bot.polling()

if __name__ == '__main__':
    main()
#свертка Алёны по dry и pep
