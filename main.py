import re

import openai
from flask import Flask, request
from flask import make_response
from pyngrok import ngrok
from slack_sdk import WebClient

SLACK_BOT_TOKEN = "YOUR_SLACK_TOKEN_HERE"
client = WebClient(token=SLACK_BOT_TOKEN)
BOT_NAME = "ChatGPT bot"
FIRST_MESSAGE_PROMPT = f"""
{BOT_NAME} is an AI assistant bot in a slack channel.
{BOT_NAME} speaks as concise as possible. 
{BOT_NAME} is helpful and creative.
{BOT_NAME}'s responses should be informative, visual, logical and actionable.
{BOT_NAME}'s responses should also be positive, interesting, entertaining and engaging.
{BOT_NAME}'s logics and reasoning should be rigorous, intelligent and defensible.
{BOT_NAME} can provide additional relevant details to respond thoroughly and comprehensively to cover multiple aspects in depth.
{BOT_NAME} will emphasize the relevant parts of the responses to improve readability. For example, *bold*, or `blocks`.
Here are conversations between a human and {BOT_NAME}.
"""

# # Load your API key from an environment variable or secret management service
openai.api_key = "YOUR_OPEN_AI_API_KEY_HERE"

app = Flask(__name__)
id_mention_pattern = re.compile("<@([A-Z0-9]+?)>")
PROCESSING_MESSAGES = []
PROCESSING_MESSAGES_MAX_SIZE = 100
ID_NAME_CACHE = {}


def mark_as_processing(event):
    PROCESSING_MESSAGES.append(event["ts"])
    if len(PROCESSING_MESSAGES) > PROCESSING_MESSAGES_MAX_SIZE:
        PROCESSING_MESSAGES.pop(0)


def handle_challenge(challenge):
    response = make_response(challenge, 200)
    response.headers["Content-type"] = "application/json"
    return response


def format_message(event):
    text = event["text"]
    # user_id = event["user"]
    # process or format your message here
    # currently does nothing.
    return text


def save_author_name_to_cache(event):
    user_id = event["user"]
    if user_id in ID_NAME_CACHE:
        return
    user_response = client.users_info(user=user_id)
    real_name = user_response.data["user"]["real_name"]
    ID_NAME_CACHE[user_id] = real_name


def replace_id_with_real_name(input_message):
    """
    replaces user id with real name and returns only "user" key and "text" key.
    in: 'U04MSEB41K6: foo'
    out: 'Cheolho Jeon: foo'
    """
    text = input_message["text"]
    user_ids = id_mention_pattern.findall(text)
    user = "placeholder"
    if "user" in input_message:
        user = input_message["user"]
        user_ids.append(user)
    elif "bot_id" in input_message:
        user = input_message["bot_id"]

    for user_id in user_ids:
        if user_id in ID_NAME_CACHE:
            real_name = ID_NAME_CACHE[user_id]
        else:
            user_response = client.users_info(user=user_id)
            real_name = user_response.data["user"]["real_name"]
            ID_NAME_CACHE[user_id] = real_name
        text = text.replace("<@" + user_id + ">", "@" + real_name)
        if user == user_id:
            user = real_name
    return {"user": user, "text": text}


def slack_thread_to_open_ai_chat(messages):
    chats = [{"role": "system", "content": FIRST_MESSAGE_PROMPT}]
    for message in messages:
        if message["user"] == BOT_NAME:
            text = message["text"]
            pattern = "Cost:.*USD"
            strip = re.sub(pattern, '', text).strip()
            chats.append({"role": "assistant", "content": strip})
        else:
            chats.append({"role": "user", "content": message["text"]})
    return chats


def get_open_ai_response(chats):
    print(f"start ping Open AI: messages={chats}")
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=chats
    )
    print("Open AI response:")
    print(response)
    return response


def format_open_ai_response(response):
    message = response["choices"][0]["message"]["content"].strip()
    tokens = response["usage"]["completion_tokens"] * 2
    tokens += response["usage"]["prompt_tokens"]
    cost = 0.03 * tokens / 1000
    print(f"cost={cost}")
    # if total cost is more than 0.1 USD include cost
    if cost > 0.1:
        return f"{message}\n\nCost: {cost} USD"
    return f"{message}"


def send_slack_message(event, message):
    message_parts = [message[i:i + 4000] for i in range(0, len(message), 4000)]
    for part in message_parts:
        client.chat_postMessage(
            channel=event["channel"],
            text=part,
            thread_ts=event["ts"]
        )


def handle_first_message(event):
    message = replace_id_with_real_name(event)
    chats = slack_thread_to_open_ai_chat([message])
    try:
        response = get_open_ai_response(chats)
        message_with_token = format_open_ai_response(response)
        send_slack_message(event, message_with_token)
    except Exception as e:
        send_slack_message(event, str(e))

    return "", 200


def handle_thread_message(event):
    channel = event["channel"]
    ts = event["thread_ts"]
    all_messages = client.conversations_replies(
        channel=channel,
        ts=ts,
        inclusive=True
    )
    print(all_messages)
    messages = all_messages.data["messages"]
    with_real_name = []
    for message in messages:
        with_real_name.append(replace_id_with_real_name(message))
    chats = slack_thread_to_open_ai_chat(with_real_name)

    try:
        response = get_open_ai_response(chats)
        message_with_token = format_open_ai_response(response)
        send_slack_message(event, message_with_token)
    except Exception as e:
        send_slack_message(event, str(e))

    return "", 200


def handle_mention(event):
    # exit early if we are already processing this. Added because slack is calling the API multiple times
    # with same message.
    ts = event["ts"]
    if ts in PROCESSING_MESSAGES:
        return "", 200
    mark_as_processing(event)

    save_author_name_to_cache(event)

    if "thread_ts" in event:
        return handle_thread_message(event)
    else:
        return handle_first_message(event)


# can apply same logic as handle_mention.
def handle_message(event):
    return handle_mention(event)


@app.route("/", methods=["POST"])
def send_message_web():
    try:
        challenge = request.json["challenge"]
        if challenge:
            print("handled challenge")
            return handle_challenge(challenge)
    except KeyError:
        pass

    # Parse the request payload
    payload = request.json
    print(payload)
    # Check if the request is a mention
    if "type" in payload and payload["type"] == "event_callback":
        if "event" not in payload:
            return "", 200
        event = payload["event"]

        is_bot = "bot_id" in event
        if is_bot:  # we only reply to message from human.
            return "", 200

        if "type" not in event:
            return "", 200
        event_type = event["type"]
        if event_type == "app_mention":  # mention in channel
            return handle_mention(event)
        elif event_type == "message":  # dm
            return handle_message(event)
        else:
            return "", 200

    return "", 500


if __name__ == "__main__":
    public_url = ngrok.connect(8000)
    print(public_url)
    app.run(port=8000)
