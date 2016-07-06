from flask.ext.wtf import Form
from wtforms import TextField

class ChatForm(Form):
    text = TextField('text')
