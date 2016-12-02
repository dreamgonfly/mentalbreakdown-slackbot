from slackclient import SlackClient
import time
from parse import filter_message, parse_message
from execute import execute_command
from config import SLACK_BOT_TOKEN, BOT_ID, READ_WEBSOCKET_DELAY

slack_client = SlackClient(SLACK_BOT_TOKEN)
if slack_client.rtm_connect():
    print("Bot connected and running!", flush=True)
    while True:
        filtered = filter(filter_message, slack_client.rtm_read())
        for message in filtered:
            print('message :', message)
            parsed_message = parse_message(message)
            print('parsed message :', parsed_message)
            response = execute_command(parsed_message)
            print('response :', response)
            slack_client.rtm_send_message(message['channel'], response)
        time.sleep(READ_WEBSOCKET_DELAY)
else:
    print("Connection failed. Invalid Slack token or bot ID?")