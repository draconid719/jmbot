import requests
import sys
from users.models import Profile
from django.contrib.auth.models import User

sys.path.append(".../users")

# Telegram bot token
TOKEN = "1243983171:AAFkTr7nz0JF8CV4Oa91KRwNjfmko4eb2Vg"


def send_telegram_message(author, text):
    g_user = User.objects.filter(pk=author).first()
    sendto = Profile.objects.filter(user=g_user).first()
    chat_id = sendto.telegram
    if chat_id is not None:
        BASE_TELEGRAM_URL = 'https://api.telegram.org/bot{}'.format(TOKEN)
        print(chat_id)
        Send_message = BASE_TELEGRAM_URL + '/sendMessage?chat_id={}&text={}'.format(chat_id, text)
        requests.get(Send_message)
