# coding: utf-8
import os
from flask import Flask, request, send_from_directory, render_template, redirect, url_for
import messenger
from config import CONFIG
from fbpage import page
from forms.question_form import QuestionForm
from forms.entitytag_form import EntityTagForm
from EntityManager import addEntity
from models import *

app = Flask(__name__)

app.config.update(dict(
    SECRET_KEY=CONFIG['SECRET_KEY'],
    WTF_CSRF_SECRET_KEY=CONFIG['WTF_CSRF_SECRET_KEY']
))

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0, parentdir)


@app.route('/index')
@app.route('/')
def index():
    return render_template('index.html')


# displays all events
@app.route('/event')
def event():
    events = list()
    events.append({'name': 'Hack the Castle', 'id': 1})
    return render_template('event.html', events=events)


# displays all participants
@app.route('/participant')
def participant():
    participants = select_participants()
    participants.append({'name': 'Tulga Ariuntuya', 'id': 2, 'fb_id': 982936161761293})
    participants.append({'name': 'Gunnar Stenlund', 'id': 3, 'fb_id': 1386169068167016})
    participants.append({'name': 'Mohamed Hassainia', 'id': 4, 'fb_id': 100013370437252})
    return render_template('participant.html', participants=participants)


# displays all questions
@app.route('/question')
def question():
    questions = select_questions()
    return render_template('questions.html', questions=questions)


# add new question forms
@app.route('/add-question', methods=['POST', 'GET'])
def add_question():
    form = QuestionForm()
    categories = list()
    categories.append({'id': 1, 'name': 'Feedback'})
    categories.append({'id': 1, 'name': 'Find team'})

    if request.method == 'POST':
        if form.validate_on_submit():
            # add question to db and display question page
            create_question(form.question_text.data)
            return redirect(url_for('question'))
        return render_template('add-question.html', categories=categories, form=form)

    # display add-question form
    return render_template('add-question.html', categories=categories, form=form)


# display all entity-tags
@app.route('/entity-tag')
def entity_tag():
    entity_tags = select_all_entitytag()
    return render_template('entitytag.html', entity_tags=entity_tags)


# add new entity-tag forms
@app.route('/add-entity-tag', methods=['POST', 'GET'])
def add_entity_tag():
    form = EntityTagForm()

    if request.method == 'POST':
        if form.validate_on_submit():

            # preprocessing data
            # not best, but works for now xD
            expressions = form.expressions.data.split(",")
            tag = form.tag_value.data

            # adding entity to fb app
            addEntity(tag, expressions)

            # add question to db and display success page
            create_entitytag(form.tag_value.data, form.expressions.data)

            return redirect(url_for('entity_tag'))

        return render_template('add-entitytag.html', form=form)

    # display add-question form
    return render_template('add-entity-tag.html', form=form)


# displaying all feedback
@app.route('/feedback', methods=['GET'])
def feedback():
    fbk = select_feedbacks()
    return render_template('feedback.html', feedback=fbk)


# set up webhooks
@app.route('/webhook', methods=['GET'])
def validate():
    if request.args.get('hub.mode', '') == 'subscribe' and \
                    request.args.get('hub.verify_token', '') == CONFIG['VERIFY_TOKEN']:

        print("Validating webhook")

        return request.args.get('hub.challenge', '')
    else:
        return 'Failed validation. Make sure the validation tokens match.'


# all event handlers on webhooks
@app.route('/webhook', methods=['POST'])
def webhook():
    payload = request.get_data(as_text=True)
    print(payload)
    page.handle_webhook(payload)
    return "ok"


@app.route('/authorize', methods=['GET'])
def authorize():
    account_linking_token = request.args.get('account_linking_token', '')
    redirect_uri = request.args.get('redirect_uri', '')

    auth_code = '1234567890'

    redirect_uri_success = redirect_uri + "&authorization_code=" + auth_code

    return render_template('authorize.html', data={
        'account_linking_token': account_linking_token,
        'redirect_uri': redirect_uri,
        'redirect_uri_success': redirect_uri_success
    })


@app.route('/assets/<path:path>')
def assets(path):
    return send_from_directory('assets', path)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5003, debug=True, threaded=True)
