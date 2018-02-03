# coding: utf-8
import os
from flask import Flask, request, send_from_directory, render_template, redirect, url_for
import messenger
from config import CONFIG
from fbpage import page
from forms.question_form import QuestionForm
from forms.entitytag_form import EntityTagForm
from models import *

app = Flask(__name__)

app.config.update(dict(
    SECRET_KEY="123456789",
    WTF_CSRF_SECRET_KEY="123456789"
))

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir)


@app.route('/index')
@app.route('/')
def hello_world():
    author = "Me"
    name = "You"
    return render_template('index.html')


@app.route('/event')
def event():
    events = list()
    events.append({'name': 'Hack the Castle', 'id': 1})
    return render_template('event.html', events=events)


@app.route('/participant')
def participant():
    participants = list()
    participants.append({'name': 'Oleksii Prykhodko', 'id': 1, 'fb_id': 100004190145019})
    participants.append({'name': 'Tulga Ariuntuya', 'id': 2, 'fb_id': 982936161761293})
    participants.append({'name': 'Gunnar Stenlund', 'id': 3, 'fb_id': 1386169068167016})
    participants.append({'name': 'Mohamed Hassainia', 'id': 4, 'fb_id': 100013370437252})
    return render_template('participant.html', participants=participants)


@app.route('/question')
def question():
    questions = list()
    questions = select_questions()
    return render_template('questions.html', questions=questions)


@app.route('/add-question', methods=['POST', 'GET'])
def add_question():
    form = QuestionForm()
    categories = list()
    categories.append({'id': 1, 'name': 'Feedback'})
    categories.append({'id': 1, 'name': 'Find team'})

    if request.method == 'POST':
        if form.validate_on_submit():
            # add question to db and display success page
            create_question(form.question_text.data)
            return redirect(url_for('question'))
        return render_template('add-question.html', categories=categories, form=form)

    # display add-question form
    return render_template('add-question.html', categories=categories, form=form)



@app.route('/entity-tag')
def entity_tag():
    entity_tags = select_all_entitytag()
    return render_template('entitytag.html', entity_tags=entity_tags)


@app.route('/add-entity-tag', methods=['POST', 'GET'])
def add_entity_tag():
    form = EntityTagForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            # add question to db and display success page
            create_entitytag(form.tag_value.data, form.expressions.data)
            return redirect(url_for('entity_tag'))
        return render_template('add-entitytag.html', form=form)

    # display add-question form
    return render_template('add-entity-tag.html', form=form)


@app.route('/test', methods=['GET'])
def test():
    q = select_questions()
    return render_template('test.html', qv=q)


@app.route('/webhook', methods=['GET'])
def validate():
    if request.args.get('hub.mode', '') == 'subscribe' and \
                    request.args.get('hub.verify_token', '') == CONFIG['VERIFY_TOKEN']:

        print("Validating webhook")

        return request.args.get('hub.challenge', '')
    else:
        return 'Failed validation. Make sure the validation tokens match.'


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
