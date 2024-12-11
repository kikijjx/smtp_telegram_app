import telebot
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re
from dotenv import load_dotenv
import os
import logging

load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.yandex.ru')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

bot = telebot.TeleBot(TOKEN)

user_state = {}

def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

def send_email(to_email, message):
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            msg = MIMEMultipart()
            msg['From'] = EMAIL_USER
            msg['To'] = to_email
            msg['Subject'] = "telegram SMPT app"
            msg.attach(MIMEText(message, 'plain'))
            server.send_message(msg)
        logging.info(f"Email sent to {to_email}")
        return True
    except Exception as e:
        logging.error(f"Error sending email: {e}")
        return False


@bot.message_handler(commands=['start'])
def start_handler(message):
    logging.info(f"User {message.chat.id} started interaction.")
    bot.send_message(message.chat.id, "Введите email:")
    user_state[message.chat.id] = {'state': 'awaiting_email'}

@bot.message_handler(func=lambda message: user_state.get(message.chat.id, {}).get('state') == 'awaiting_email')
def email_handler(message):
    email = message.text.strip()
    if is_valid_email(email):
        user_state[message.chat.id]['email'] = email
        user_state[message.chat.id]['state'] = 'awaiting_message'
        logging.info(f"User {message.chat.id} provided a valid email: {email}")
        bot.send_message(message.chat.id, "Введите текст сообщения:")
    else:
        logging.warning(f"User {message.chat.id} provided an invalid email: {email}")
        bot.send_message(message.chat.id, "Некорректный email.")

@bot.message_handler(func=lambda message: user_state.get(message.chat.id, {}).get('state') == 'awaiting_message')
def message_handler(message):
    email = user_state[message.chat.id]['email']
    text_message = message.text.strip()
    if send_email(email, text_message):
        bot.send_message(message.chat.id, "Сообщение отправлено.")
    else:
        bot.send_message(message.chat.id, "Ошибка при отправке.")
    bot.send_message(message.chat.id, "1. Новое сообщение\n2. Изменить email")
    user_state[message.chat.id]['state'] = 'awaiting_next_action'

@bot.message_handler(func=lambda message: user_state.get(message.chat.id, {}).get('state') == 'awaiting_next_action')
def next_action_handler(message):
    choice = message.text.strip()
    if choice == '1':
        user_state[message.chat.id]['state'] = 'awaiting_message'
        bot.send_message(message.chat.id, "Введите текст сообщения:")
    elif choice == '2':
        user_state[message.chat.id]['state'] = 'awaiting_email'
        bot.send_message(message.chat.id, "Введите email:")
    else:
        bot.send_message(message.chat.id, "Введите 1 или 2.")

if __name__ == '__main__':
    logging.info("Bot started.")
    bot.polling(none_stop=True)
