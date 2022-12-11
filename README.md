# Pyobigram
Python 3 library for making fast telegram bots
# Description
Pyobigram is a fast library for telegram bots , mtproto update, author : Obisoft
# Features v2.1.0
- Suport Handle Messages (all_messages,cmd_message,inline_message,callback_message)
- Suport Send & Edit & Delete (Messages)
- Suport Forward Messages
- Suport Upload & Download Files MtProto (max 2gb)
- Suport AnswerInline (InlineArticle,InlineDocument)
- Suport Send Reply Narkup Buttons
# Quickstart & Installation
Pyobigram requires an installation of Python 3.6 or greater, as well as pip. (Pip is typically bundled with Python 
To install from the source with pip:
```
pip install https://github.com/ObisoftDev/pyobigram/archive/master.zip
```
- Using pyobigram in a Python script
```
from pyobigram.client import ObigramClient

bot_token = 'BOT_TOKEN'
api_id = 'API_ID'
api_hash = 'API_HASH'

def message_handle(update,bot:ObigramClient):
	#TODO message handle functions
	pass

if __name__ == '__main__':
    bot = ObigramClient(bot_token,api_id=api_id,api_hash=api_hash)
    bot.onMessage(message_handle)
    print('bot is runing!')
    bot.run()
```
