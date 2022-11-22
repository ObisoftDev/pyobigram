#Inline Buttons
def inlineKeyboardMarkup(**params):
    buttons = []
    for item in params:
        buttons.append(params[item])
    return {'inline_keyboard':buttons}

def inlineKeyboardMarkupArray(paramms):
    return {'inline_keyboard':paramms}

def inlineKeyboardButton(text='text',url='',callback_data=''):
    result = {'text':text}
    if url!='':
       result['url'] = url
    if callback_data!='':
       result['callback_data'] = callback_data
    return result

#Inline Queries
def inlineQueryResultArticle(id=0,title='',
                             text='',
                             url='',hide_url=False,
                             thumb_url='',
                             thumb_width=10,thumb_height=10,
                             parse_mode=''):
    result = {'type':'article',
            'id':id,
            'title':title,
            'input_message_content':{'message_text':text},
            'url':url,
            'hide_url':hide_url,
            'thumb_url':thumb_url,
            'thumb_width':thumb_width,
            'thumb_height':thumb_height}
    if parse_mode!='':
        result['parse_mode'] = parse_mode
    return result

def inlineQueryResultDocument(id=0,title='',
                              caption='',text='',description='',
                              url='',hide_url=False,
                              thumb_url='',
                              thumb_width=10,thumb_height=10,
                              parse_mode=''):
    result = {'type':'article',
            'id':id,
            'title':title,
            'input_message_content':{'message_text':text},
            'document_url':url,
            'hide_url':hide_url,
            'thumb_url':thumb_url,
            'thumb_width':thumb_width,
            'thumb_height':thumb_height}
    if parse_mode!='':
        result['parse_mode'] = parse_mode
    return result