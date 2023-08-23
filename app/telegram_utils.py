from re import T
import telegram
from dotenv import load_dotenv
import os
from os.path import join, dirname

current_file = os.path.abspath(os.path.dirname(__file__))
parent_of_parent_dir = os.path.join(current_file, '../')
dotenv_path = join(parent_of_parent_dir, '.env')
load_dotenv(dotenv_path)

bot = telegram.Bot(token=os.environ.get("TOKEN"))

def send_telegram(photo_path="alert.png"):
    try:
        bot.sendPhoto(chat_id=os.environ.get("CHAT_ID"), photo=open(
            photo_path, "rb"), caption="Phát hiện hành vi bạo lực")
        print("Send sucess")
    except Exception as ex:
        print(ex)


if __name__ == "__main__":
    send_telegram()
