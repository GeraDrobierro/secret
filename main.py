import telebot
import sqlite3
from telebot import types
import os

bot = telebot.TeleBot(token='7175694691:AAGbBUhvNaKbC93_BSQynmzSeu5GCV_NAGo')
name = None
artist = None
old_name = None

def main():
    """
    @brief Main function to run the bot and initialize handlers.
    """

    def get_playlist_info():
        """
        @brief Fetches playlist information from the database.
        @return A string containing the playlist info.
        """
        conn = sqlite3.connect('music.sql')
        cur = conn.cursor()
        cur.execute('SELECT * FROM loadings')
        loadings = cur.fetchall()
        cur.close()
        conn.close()
        info = '\n'.join(f'Название трека: {i[1]}, Исполнитель: {i[2]}' for i in loadings)
        return info

    def create_main_markup():
        """
        @brief Creates the main markup for the bot's reply keyboard.
        @return markup object containing buttons.
        """
        markup = types.ReplyKeyboardMarkup()
        btn_list = ['/listen', '/add', '/view_all', '/options']
        for btn in btn_list:
            markup.row(types.KeyboardButton(btn))
        return markup

    def send_playlist(message):
        """
        @brief Sends the playlist information to the user.
        @param message The message object from the user.
        """
        info = get_playlist_info()
        bot.send_message(message.chat.id, 'ВАШ ПЛЕЙЛИСТ:')
        bot.send_message(message.chat.id, info)

    def start_message(message, text):
        """
        @brief Sends a start message to the user along with the main markup.
        @param message The message object from the user.
        @param text The text to be sent.
        """
        bot.send_message(message.chat.id, text, reply_markup=create_main_markup())

    @bot.message_handler(commands=['help'])
    def help_message(message):
        """
        @brief Handles the /help command and sends help information to the user.
        @param message The message object from the user.
        """
        with open('help.txt', 'r') as file:
            k = file.read()
        start_message(message, k)

    @bot.message_handler(commands=['start'])
    def start(message):
        """
        @brief Handles the /start command and sends a greeting to the user.
        @param message The message object from the user.
        """
        start_message(message, f'Привет, {message.from_user.first_name}, напиши /help')

    @bot.message_handler(commands=['listen'])
    def listen(message):
        """
        @brief Handles the /listen command, prompts for a track, and plays it.
        @param message The message object from the user.
        """
        try:
            send_playlist(message)
            bot.register_next_step_handler(message, music_player)
        except sqlite3.OperationalError:
            bot.send_message(message.chat.id, 'Ты пока не загрузил песни')

    def music_player(message):
        """
        @brief Plays the requested track for the user.
        @param message The message object from the user.
        """
        conn = sqlite3.connect('music.sql')
        cur = conn.cursor()
        checkout = message.text
        cur.execute('SELECT * FROM loadings WHERE name=?', (checkout,))
        track = cur.fe
