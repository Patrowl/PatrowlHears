from django.conf import settings
from slack import WebClient
from slack.errors import SlackApiError
import logging
logger = logging.getLogger(__name__)


def get_slack_channel_id(name, slack_client, force=True):
    print("in get_slack_channel_id()")
    channel_id = None
    try:
        response = slack_client.conversations_list()
        print("response:", response)
    except SlackApiError as e:
        assert e.response["ok"] is False
        logger.error(f"Got an error: {e.response['error']}")
        return None
    for chan in response['channels']:
        print(chan)
        if chan['name'] == name:
            channel_id = chan['id']
            break
    
    if channel_id is None and force is True:
        print("create a new channel")
        channel_id = create_slack_channel(name, slack_client)
    
    return channel_id


def create_slack_channel(name, slack_client):
    try:
        response = slack_client.conversations_create(name=name)
    except SlackApiError as e:
        assert e.response["ok"] is False
        logger.error(f"Got an error: {e.response['error']}")
        return None
    print("create_slack_channel/channel_id:", response['id'])
    return response['id']


def send_slack_message(message, apitoken, channel):
    slack_client = WebClient(token=apitoken)
    channel_id = get_slack_channel_id(channel, slack_client)
    print("send_slack_message/channel_id:", channel_id)
    try:
        slack_client.chat_postMessage(
            channel=channel_id,
            text=message)
        return True
    except SlackApiError as e:
        assert e.response["ok"] is False
        assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
        logger.error(f"Got an error: {e.response['error']}")
        return False