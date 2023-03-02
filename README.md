# Simple-Chat-GPT-Slack-Bot

Simple script to add Chat GPT to your slack workspace.  
한국어 설명이 하단에 있습니다.

# Instructions:
You will need to 1. create a slack bot, 2. open an Open AI account to use this script.

## Slack Bot creation
1. Create your Slack app here: [Slack](https://api.slack.com/apps)
2. In OAuth & permissions page, grant below permissions
```
app_mentions:read
channels:history
chat:write
groups:history
im:history
incoming-webhook
mpim:history
users:read
```
3. Add your bot to a channel.
4. set `SLACK_BOT_TOKEN` in `main.py`.

## Open AI
1. Go to [Open AI](https://platform.openai.com/), create your account.
2. Visit [Open AI API key](https://platform.openai.com/account/api-keys) page, view your API key.
3. set `openai.api_key` in `main.py`.

## Run it
1. Run `main.py`. It will print ngrok url.
2. Go to `Event Subscriptions` page of your slack app. Enable `Enable Events`. 
3. Copy-paste your ngrok url to `Request URL`.
4. In the channel you enabled to bot, mention the bot and send a message. (you must mention the bot)

## Extra
You must mention the bot to trigger the bot.
The bot can also reply in thread (if mentioned).

# 한국어:
1. 슬랙 봇을 생성, 설정하시고,
2. Open AI 계정을 연결하시면 됩니다.

## 슬랙 봇 생성
1. 다음 링크에서 슬랙 봇을 생성하세요: [Slack](https://api.slack.com/apps)
2. OAuth & permissions 페이지에서 아래 권한을 부여하세요.
```
app_mentions:read
channels:history
chat:write
groups:history
im:history
incoming-webhook
mpim:history
users:read
```
3. 봇을 원하시는 페이지에 초대하세요.
4. `main.py`에서 `SLACK_BOT_TOKEN`을 설정하세요.

## Open AI
1. [Open AI](https://platform.openai.com/)에서 계정을 생성하세요.
2. [Open AI API key](https://platform.openai.com/account/api-keys)에서 API key 를 조회하세요.
3. `main.py`에서 `openai.api_key`를 설정하세요.

## 실행
1. `main.py`를 실행하세요. ngrok URL 이 나올 겁니다.
2. 슬랙 앱에서 `Event Subscriptions` 페이지로 가신 뒤, `Enable Events` 를 켜세요.
3. `Request URL` 에 ngrok URL 을 붙여넣으세요.
4. 봇을 초대하신 채널에서 봇을 멘션하는 메시지를 보내시면 봇이 대답합니다.

## Extra
봇을 멘션하셔야지 봇이 응답합니다.
쓰레드에서도 봇을 멘션하셔야 봇이 응답합니다.

# AD / 광고
VTOV 는 수도권 당일배송 서비스 Today 를 운영하는 IT 기반 물류 스타트업입니다.  
> 사람은 수도권이라면 어디에서 출발하든, 어디로 가든 24시간 내에 이동할 수 있는데 왜 택배는 그러지 못할까요?  

저희는 이런 질문으로 시작해 현재 서울 모든 구에 당일배송 서비스를 제공하고 있습니다.  
많은 관심 부탁드립니다.  

https://www.amazing.today/

VTOV is a logistics startup operating the same-day delivery service "Today" in the Seoul metropolitan area.

> People can travel anywhere within 24 hours regardless of where they depart from or where they go in the Seoul metropolitan area. So why can't delivery services do the same?

We started with this question and are currently providing same-day delivery service to all districts in Seoul. Thank you for your interest.

https://www.amazing.today/
