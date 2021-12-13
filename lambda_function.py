#import json
import requests
import os
import boto3

URL = f"https://api.telegram.org/bot{os.environ['AWS_BOT_TOKEN']}/"

def send_message(text, chat_id):
    final_text = "Вы написали: " + text
    url = URL + "sendMessage?text={}&chat_id={}".format(final_text, chat_id)
    requests.get(url)

def lambda_handler(event, context):

    message = event
    chat_id = message['message']['chat']['id']
    reply = message['message']['text']
    send_message(reply, chat_id)  
    print(message)
    print(reply)
    return {
        'statusCode': 200
    }
