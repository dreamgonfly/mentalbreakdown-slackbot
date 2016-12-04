from slackclient import SlackClient
import time
from parse import filter_message, parse_message, preprocess
from execute import execute_command
from config import SLACK_BOT_TOKEN, BOT_ID, READ_WEBSOCKET_DELAY

slack_client = SlackClient(SLACK_BOT_TOKEN)
if slack_client.rtm_connect():
    print("Bot connected and running!", flush=True)
    last_task = None
    while True:
        filtered = filter(filter_message, slack_client.rtm_read())
        for message in filtered:
            if message['text'] == '닫혀라 참깨': assert False
            try:
                print('message :', message)
                parsed_message = parse_message(message)
                parsed_message = preprocess(parsed_message, last_task)
                print('parsed message :', parsed_message)
                response, last_task = execute_command(parsed_message)
                print('response :', response)
            except Exception as e:
                print(e)
                response = "Sorry, I didn't quite get that. Type 'help' for instruction."
            slack_client.rtm_send_message(message['channel'], response)
        time.sleep(READ_WEBSOCKET_DELAY)
else:
    print("Connection failed. Invalid Slack token or bot ID?")