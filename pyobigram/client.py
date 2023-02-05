import requests
import json
import threading
try:
    from types import SimpleNamespace as Namespace
except ImportError:
    from argparse import Namespace
import time
import codecs
import uuid
import os

from .threads import ObigramThread
from .utils import get_url_file_name,req_file_size,createID,makeSafeFilename
from .readers import FileProgressReader,FileUrlProgressReader

from typing import Dict, cast
from telethon.tl.custom import Message
from telethon.tl.types import TypeInputPeer, InputPeerChannel, InputPeerChat, InputPeerUser

from telethon import TelegramClient
from telethon.tl.types import InputDocument
from telethon import functions, types
from .paralleltransfer import download_file,create_stream

import asyncio

class ObigramClient(object):
    def __init__(self,token,api_id='',api_hash=''):
        self.token = token
        self.path = 'https://api.telegram.org/bot' + token + '/'
        self.files_path = 'https://api.telegram.org/file/bot' + token + '/'
        self.runing = False
        self.funcs = {}
        self.update_id = 0
        self.onmessage = None
        self.oninline = None
        self.SendFileTypes = {'document':'SendDocument','video':'SendVideo'}
        self.this_thread = None
        self.threads = {}
        # api telegram mtproto
        self.api_id = api_id
        self.api_hash = api_hash
        self.mtproto = None
        self.transfer = None
        self.loop = None
        self.Way = False
        self.store = {}
        self.callback_funcs = {}
        self.temps = []

    def newMTP(self,name='obigram'):
        if self.api_id!='' and self.api_hash!='':
            try:
                os.unlink(f'{name}.session')
                os.unlink(f'{name}.session-journal')
            except:pass
            self.mtproto = TelegramClient(name,api_id=self.api_id,api_hash=self.api_hash)
            self.mtproto.start(bot_token=self.token)
            try:
                    self.loop = asyncio.get_runing_loop();
            except:
                    try:
                        self.loop = asyncio.get_event_loop();
                    except:pass
        
    def startNewThread(self,targetfunc=None,args=(),update=None):
        self.this_thread = ObigramThread(targetfunc=targetfunc,args=args,update=update)
        self.threads[self.this_thread.id] = self.this_thread
        self.this_thread.start()
        pass

    def parseUpdate(self,update):
        parse = str(update).replace('sender_chat','chat')
        parse = str(parse).replace('from','sender')
        parse = str(parse).replace('my_chat_member','message')
        parse = str(parse).replace('document','file')
        parse = str(parse).replace('video','file')
        parse = str(parse).replace('photo','file')
        return parse

    def way(self,way=False):self.Way=way

    def run_forever_loop(self,args=None):
        #self.loop.run_forever()
        pass

    def run(self):
        self.newMTP()
        self.runing = True
        if self.loop:
            self.startNewThread(self.run_forever_loop)
        while self.runing:
            while self.Way==True:pass
            try:
                getUpdateUrl = self.path + 'getUpdates?offset=' + str(self.update_id+1)
                update = requests.get(getUpdateUrl)
                update = self.parseUpdate(str(update.text))
                updates = json.loads(update, object_hook = lambda d : Namespace(**d)).result

                if len(updates) > 0:
                    self.update_id = updates[-1].update_id

                try:
                    for func in self.funcs:
                        for update in updates:
                                if func in update.message.text:
                                    self.startNewThread(self.funcs[func],(update,self),update)
                except:pass

                try:
                        for update in updates:
                            try:
                                if update.inline_query:
                                    if self.oninline:
                                        self.startNewThread(self.oninline,(update,self),update)
                                    break
                            except:
                                try:
                                    if update.callback_query:
                                        for callback in self.callback_funcs:
                                            if callback in update.callback_query.data:
                                                update.callback_query.data = str(update.callback_query.data).replace(callback,'')
                                                self.startNewThread(self.callback_funcs[callback],
                                                                    (update.callback_query, self),
                                                                    update.callback_query)
                                                break
                                except:
                                    if self.onmessage:
                                        self.startNewThread(self.onmessage,(update,self),update)
                except Exception as ex:print(str(ex))

            except Exception as ex:
                print(str(ex))
            pass
        self.threads.clear()
        pass

    def send_message(self,chat_id=0,text='',parse_mode='',reply_markup=None,reply_to_message_id=None):
        try:
            text=text.replace('%', '%25')
            text=text.replace('#', '%23')
            text=text.replace('+', '%2B')
            text=text.replace('*', '%2A')
            text=text.replace('&', '%26')
            sendMessageUrl = self.path + 'sendMessage?chat_id=' + str(chat_id) + '&text=' + text + '&parse_mode=' + parse_mode
            payload = {'reply_markup': reply_markup}
            jsonData = {}
            if reply_to_message_id:
                payload['reply_to_message_id'] = reply_to_message_id
                jsonData['reply_to_message_id'] = reply_to_message_id
            if reply_markup:
                jsonData = payload
            result = requests.get(sendMessageUrl,json=jsonData).text
            result = self.parseUpdate(result)
            return json.loads(result, object_hook = lambda d : Namespace(**d)).result
        except Exception as ex:
            print(str(ex))
            pass
        return None

    def delete_message(self,message):
        try:
            deleteMessageUrl = self.path + 'deleteMessage?chat_id='+str(message.chat.id)+'&message_id='+str(message.message_id)
            result = requests.get(deleteMessageUrl).text
            result = self.parseUpdate(result)
            return json.loads(result, object_hook = lambda d : Namespace(**d)).result
        except:pass
        return None

    def edit_message(self,message,text='',parse_mode='',reply_markup=None):
        if message:
            try:
                text=text.replace('%', '%25')
                text=text.replace('#', '%23')
                text=text.replace('+', '%2B')
                text=text.replace('*', '%2A')
                text=text.replace('&', '%26')
                editMessageUrl = self.path+'editMessageText?chat_id='+str(message.chat.id)+'&message_id='+str(message.message_id)+'&text=' + text + '&parse_mode=' + parse_mode
                payload = {'reply_markup': reply_markup}
                jsonData = {}
                if reply_markup:
                    jsonData = payload
                result = requests.get(editMessageUrl,json=jsonData).text
                result = self.parseUpdate(result)
                parse = json.loads(result, object_hook = lambda d : Namespace(**d))
                sussesfull = False
                try: 
                    sussesfull = parse.ok and parse.result 
                    if sussesfull == False:
                         print('Warning EditMessage: '+str(parse.description))
                except: pass
                message.text = text
                return message
            except: pass
        return None


    def send_file(self,chat_id,file,type='document',caption=None,reply_to_message_id=None,reply_markup=None,thumb=None):
        sendDocumentUrl = self.path + self.SendFileTypes[type]
        of = codecs.open(file)
        if thumb:
            thumbfile = codecs.open(thumb)
        payload_files = {type:(file,of)}
        payload_data = {'chat_id':chat_id}
        if thumb:
            payload_files['thumb'] = (thumb,thumbfile)
        if reply_to_message_id:
            payload_data['reply_to_message_id'] = reply_to_message_id
        if reply_markup:
            payload_data['reply_markup'] = reply_markup
        if caption:
            payload_data['caption'] = caption
        result = requests.post(sendDocumentUrl,files=payload_files,data=payload_data).text
        result = self.parseUpdate(result)
        of.close()
        if thumb:
            thumbfile.close()
        parse = json.loads(result, object_hook = lambda d : Namespace(**d))
        return parse.result

    def get_file(self,file_id):
        getFileUrl = self.path + 'getFile?file_id=' + str(file_id)
        result = requests.get(getFileUrl).text
        result = self.parseUpdate(result)
        parse = json.loads(result, object_hook = lambda d : Namespace(**d)).result
        return parse

    def download_file(self,file_id=0,destname='',progressfunc=None,args=None):
        reqFile = self.getFile(file_id)
        downloadUrl = self.files_path + str(reqFile.file_path)
        req = requests.get(downloadUrl, stream = True,allow_redirects=True)
        if req.status_code == 200:
            file_wr = open(destname,'wb')
            chunk_por = 0
            chunkrandom = 100
            total = reqFile.file_size
            time_start = time.time()
            time_total = 0
            size_per_second = 0
            for chunk in req.iter_content(chunk_size = 1024):
                    chunk_por += len(chunk)
                    size_per_second+=len(chunk);
                    tcurrent = time.time() - time_start
                    time_total += tcurrent
                    time_start = time.time()
                    file_wr.write(chunk)
                    if time_total>=1:
                        if progressfunc:
                            progressfunc(destname,chunk_por,total,size_per_second,args)
                        time_total = 0
                        size_per_second = 0
            file_wr.close()
        return destname

    def mtp_download_file(self,message,dest_path='',progress_func=None,progress_args=None):
        async def asyncexec_download():
            peer = InputPeerUser(user_id=message.chat.id, access_hash=0)
            forward = cast(Message, await self.mtproto.get_messages(entity=peer, ids=message.message_id))
            #forward = await self.mtproto.forward_messages(message.sender.id,message.message_id,from_peer=message.sender.id)
            #await forward.delete()
            filename = forward.file.id + forward.file.ext
            fsize = forward.file.size
            if forward.file.name:
                filename = forward.file.name
            filename = makeSafeFilename(filename)
            output = dest_path
            if '/' in output:
                output += '/'
            output += filename
            await download_file(self.mtproto,forward.media,output,fsize,progress_func,progress_args,self)
            self.store[message.message_id] = output
        self.loop.run_until_complete(asyncexec_download())
        output = None
        while not output:
            try:
                output = self.store[message.message_id]
                self.store.pop(message.message_id)
            except:pass
            pass
        return output

    async def async_get_file_info(self,message):
        peer = InputPeerUser(user_id=message.chat.id, access_hash=0)
        forward = cast(Message, await self.mtproto.get_messages(entity=peer, ids=message.message_id))
        # forward = await self.mtproto.forward_messages(message.sender.id,message.message_id,from_peer=message.sender.id)
        # await forward.delete()
        filename = forward.file.id + forward.file.ext
        fsize = forward.file.size
        if forward.file.name:
            filename = forward.file.name
        filename = makeSafeFilename(filename)
        return {'fname':filename,'fsize':fsize,'location':message}

    def mtp_get_file_info(self,message):
        async def asyncexec_download():
            peer = InputPeerUser(user_id=message.chat.id, access_hash=0)
            forward = cast(Message, await self.mtproto.get_messages(entity=peer, ids=message.message_id))
            #forward = await self.mtproto.forward_messages(message.sender.id,message.message_id,from_peer=message.sender.id)
            #await forward.delete()
            filename = forward.file.id + forward.file.ext
            fsize = forward.file.size
            if forward.file.name:
                filename = forward.file.name
            filename = makeSafeFilename(filename)
            self.store[message.message_id] = {'fname':filename,'fsize':fsize,'location':message}
        self.loop.run_until_complete(asyncexec_download())
        output = None
        while not output:
            try:
                output = self.store[message.message_id]
                self.store.pop(message.message_id)
            except:pass
            pass
        return output

    def mtp_gen_message(self,chat_id,msg_id):
        class Chat(object):
            def __init__(self, id):
                self.id = id
                pass
        class Message(object):
            def __init__(self,chat_id,msg_id):
                self.chat = Chat(chat_id)
                self.message_id = msg_id
                pass
        return Message(chat_id,msg_id)

    async def async_get_info_stream(self,message):
        peer = InputPeerUser(user_id=message.chat.id, access_hash=0)
        forward = cast(Message, await self.mtproto.get_messages(entity=peer, ids=message.message_id))
        # forward = await self.mtproto.forward_messages(message.sender.id,message.message_id,from_peer=message.sender.id)
        # await forward.delete()
        filename = forward.file.id + forward.file.ext
        fsize = forward.file.size
        if forward.file.name:
            filename = forward.file.name
        filename = makeSafeFilename(filename)
        body = create_stream(self.mtproto, forward.media, fsize)
        return {'fname':filename,'body':body,'fsize':fsize}

    def mtp_gen_stream(self,message):
        async def asyncexec_download():
            peer = InputPeerUser(user_id=message.chat.id, access_hash=0)
            forward = cast(Message, await self.mtproto.get_messages(entity=peer, ids=message.message_id))
            #forward = await self.mtproto.forward_messages(message.sender.id,message.message_id,from_peer=message.sender.id)
            #await forward.delete()
            filename = forward.file.id + forward.file.ext
            fsize = forward.file.size
            if forward.file.name:
                filename = forward.file.name
            filename = makeSafeFilename(filename)
            body = create_stream(self.mtproto,forward.media,fsize)
            self.store[message.message_id] = {'fname':filename,'body':body,'fsize':fsize}
        self.loop.run_until_complete(asyncexec_download())
        output = None
        while not output:
            try:
                output = self.store[message.message_id]
                self.store.pop(message.message_id)
            except:pass
            pass
        return output

    def mtp_send_file(self,sender,filepath,progress_func=None,progress_args=None):
        upload_id = createID()
        async def asyncexec_upload():
            file = FileProgressReader(filepath,progress_func=progress_func,progress_args=progress_args,self_in=self,normalize=True)
            send = await self.mtproto.send_file(sender.id,file)
            self.store[upload_id] = send
            pass
        self.loop.run_until_complete(asyncexec_upload())
        output = None
        while not output:
            try:
                output = self.store[upload_id]
            except:pass
            pass
        return output

    def mtp_send_file_from_url(self,sender,url,progress_func=None,progress_args=None):
        upload_id = createID()
        async def asyncexec_upload():
            file = FileUrlProgressReader(url=url,progress_func=progress_func,progress_args=progress_args,self_in=self)
            send = await self.mtproto.send_file(sender.id,file)
            self.store[upload_id] = send
            pass
        self.loop.run_until_complete(asyncexec_upload())
        output = None
        while not output:
            try:
                output = self.store[upload_id]
            except:pass
            pass
        return output

    def forward_message(self,sender_id,message):
        async def asyncexec_forward():
            forward = await self.mtproto.forward_messages(sender_id,message.message_id,from_peer=message.sender.id)
            self.store[sender_id] = forward
            pass
        self.loop.run_until_complete(asyncexec_forward())
        forward = None
        while not forward:
            try:
                forward = self.store[sender_id]
                self.store.pop(sender_id)
            except:pass
            pass
        return forward

    def answer_inline(self,inline_query_id=0,result=[]):
        answerUrl = self.path + 'answerInlineQuery'
        payload = { 'inline_query_id' : inline_query_id,'results':result}
        result = requests.post(answerUrl,json=payload).text
        result = self.parseUpdate(result)
        parse = json.loads(result, object_hook = lambda d : Namespace(**d))
        sussesfull = False
        try: 
            sussesfull = parse.ok and parse.result 
            if sussesfull == False:
                 print('Error InlineAnswer: '+str(parse.description))
        except: pass
        return sussesfull

    def contain_file(self,message):
        try:
            if message.file:
                return True
        except:pass
        return False

    def on (self,cmd,func):self.funcs[cmd] = func
    def onMessage (self,func):self.onmessage = func
    def onInline(self,func):self.oninline = func
    def onCallbackData(self,callback_data,func):self.callback_funcs[callback_data] = func
