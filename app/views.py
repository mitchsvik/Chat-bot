from flask import render_template, redirect, session
from app import app
from forms import ChatForm
import random

dictionary = {
            'positive': ['yes', 'yep', 'greetings', 'hi', 'hello', 'alloha', 'salam'],
            'negative': ['no', 'nope', 'not', 'bye'],
            'simple': ['It\'s interesting. Continue.',
                       'Want something else to talk?',
                       'You are good interlocutor.',
                       'How many facts.',
                       'I can listen this all day'],
            'joke': ['Where is my legs? I don\'t have a legs!',
                     'I think you should go to doctor. You speak with computer!',
                     'Ohh new cookies.',
                     'I work on cookies. :)',
                     'Don\'t tell anyone, but i am a robot.',
                     'Look! Food particles in your keyboard opened a space program.']
        }

@app.route('/', methods = ['GET','POST'])
@app.route('/index', methods = ['GET','POST'])
def index():
    form = ChatForm()
    if form.validate_on_submit():
        if session['start']:
            session['log'] += first_dialog(form.text.data)
            session['start'] = False
        else:
            session['log'] += continue_dialog(form.text.data)
        form.text.data = ''
        render_template('index.html', form = ChatForm(), messages = session['log'])
    else:
        session['log'] = ['Greetings, friend', 'Do you want to speak with me? :)']
        session['start'] = True
    return render_template('index.html', form = form, messages = session['log'])

def first_dialog(text):
        dialog = ['User: {}'.format(text)]
        text = text.lower()
        positive, negative = False, False
        for accept in dictionary['positive']:
            if accept in text:
                positive = True
        for denial in dictionary['negative']:
            if denial in text:
                negative = True
        if (positive and negative) or (not positive and not negative):
            dialog += ['Sorry, I could not understand you']
        elif positive:
            dialog += ['Very good. I like to speak with people.','Tell something about you.']
        else:
            dialog += ['I am upset.',' But you could find me here at any moment :)']
        return dialog

def continue_dialog(text):
        dialog = ['User: {}'.format(text)]
        text = text.lower()
        if random.randint(0,100) > 50:
            dialog += ['{}'.format(dictionary['joke'][random.randint(0, len(dictionary['joke'])-1)])]
        dialog += ['{}'.format(dictionary['simple'][random.randint(0,len(dictionary['simple'])-1)])]
        return dialog

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404
