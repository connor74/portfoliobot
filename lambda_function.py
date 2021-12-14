import requests
import os
import boto3

mime_type = {
    'text/comma-separated-values': 'csv',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'xlsx',
    'application/vnd.ms-excel': 'xls'
}


class TeleBOT:

    def __init__(self, token, data):
        self.doc_type = None
        self.token = token

        self.user_id = data['message']['from']['id']
        self.chat_id = data['message']['chat']['id']
        self.message = data['message']
        self.telegram_url = f"https://api.telegram.org/bot{token}/"
        self.answer = {
            "start": "Привет! Я\n*PortfolioBot*",
            "help": "*PortfolioBot*\n\nБот отслеживающий данные по портфелю ценных бумаг",
        }
        if "text" in self.message:
            self.message_type = "text"
        elif "document" in self.message:
            self.message_type = "document"
            self.doc_type = mime_type[self.message['document']['mime_type']]
        elif "location" in self.message:
            self.message_type = "location"
        else:
            self.message_type = None

    def send_message(self, message):
        if self.message.strip() in ["/start", "/help"]:
            message_out = self.answer[self.message[1:]]
        else:
            message_out = message

        url = f"{self.telegram_url}sendMessage?text={message_out}&chat_id={self.chat_id}"
        requests.get(url)


def upload_csv(url, user_id):
    params = {"public_key": url}
    link = requests.get(os.environ['YANDEX_DISC_URL'], params=params).json()['href']
    r = requests.get(link, stream=True)

    s3 = boto3.client('s3', aws_access_key_id=os.environ['KEY_ID'],
                      aws_secret_access_key=os.environ['SECRET_KEY'])

    s3.upload_fileobj(r.raw, "telegram-portfolio", f"user_{user_id}.csv")




def lambda_handler(event, context):
    bot = TeleBOT(os.environ['AWS_BOT_TOKEN'], event)
    if "http" in bot.message:
        print(bot.message)
        link = [text for text in bot.message.split() if text.startswith('http')][0]
        upload_csv(link, bot.user_id)
        bot.send_message("Файл загружен!")
    else:
        bot.send_message(bot.message, bot.chat_id)
    print(event)
    return {
        'statusCode': 200,
        'event': event
    }
