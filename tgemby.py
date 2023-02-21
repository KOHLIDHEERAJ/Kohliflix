import telebot
import requests
import json

# Inisialisasi bot Telegram
bot = telebot.TeleBot('TOKEN_BOT_TELEGRAM')

# Inisialisasi API Emby
EMBY_API_KEY = 'API_KEY_EMBy'
EMBY_SERVER = 'http://localhost:8096'

# Fungsi untuk mengunduh film dari server Emby
def download_movie(movie_id, chat_id):
    url = EMBY_SERVER + '/emby/Items/' + movie_id + '/Download?api_key=' + EMBY_API_KEY
    response = requests.get(url)
    if response.status_code == 200:
        file_url = json.loads(response.text)['url']
        file_name = json.loads(response.text)['name']
        response = requests.get(file_url)
        if response.status_code == 200:
            with open(file_name, 'wb') as f:
                f.write(response.content)
            bot.send_document(chat_id, open(file_name, 'rb'))
        else:
            bot.send_message(chat_id, 'Gagal mengunduh file')
    else:
        bot.send_message(chat_id, 'Gagal mengunduh file')

# Fungsi untuk menangani pesan yang diterima
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, 'Selamat datang di bot Emby!')
    bot.reply_to(message, 'Ketik /list untuk melihat daftar film yang tersedia')

@bot.message_handler(commands=['list'])
def list_movies(message):
    url = EMBY_SERVER + '/emby/Items?api_key=' + EMBY_API_KEY + '&Recursive=true&IncludeItemTypes=Movie'
    response = requests.get(url)
    if response.status_code == 200:
        movies = json.loads(response.text)['Items']
        for movie in movies:
            movie_id = movie['Id']
            movie_title = movie['Name']
            bot.send_message(message.chat.id, movie_title + ': /download_' + movie_id)
    else:
        bot.send_message(message.chat.id, 'Gagal mendapatkan daftar film')

@bot.message_handler(commands=['download'])
def download_movie_command(message):
    movie_id = message.text.split('_')[1]
    download_movie(movie_id, message.chat.id)

# Jalankan bot Telegram
bot.polling()
