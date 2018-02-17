# coding: utf-8
import os
from flask import Flask, request, send_from_directory, render_template, redirect, url_for, session
import messenger
from config import CONFIG
from fbpage import page
from forms.create_forms import InfoForm, QuestionForm, EntityTagForm, QuestionnaireForm
from models.all_models import *
from WitClient import WitClient
from models.DataBase import DataBase

DataBase.generate()
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
    if 'count' in session:
        session['count'] += 1
    else:
        session['count'] = 0
    return render_template('index.html', count=session['count'])


# --------- Event -------
# displays all events
@app.route('/event')
def event():
    events = list()
    events.append({'name': 'Hack the Castle', 'id': 1})
    return render_template('event.html', events=events)
# --------- end Event -------


# --------- Participant -------
# displays all participants
@app.route('/participant')
def participant():
    participants = Participant.select_all_participants()
    participants.append({'name': 'Tulga Ariuntuya', 'id': 2, 'fb_id': 982936161761293})
    participants.append({'name': 'Gunnar Stenlund', 'id': 3, 'fb_id': 1386169068167016})
    participants.append({'name': 'Mohamed Hassainia', 'id': 4, 'fb_id': 100013370437252})

    return render_template('participant.html', participants=participants)
# --------- end Participant -------


# --------- Questions -------
# displays all questions
@app.route('/question')
def question():
    questions = Question.select_all_questions()
    return render_template('questions.html', questions=questions)


# add new question forms
@app.route('/add-question', methods=['POST', 'GET'])
def add_question():
    form = QuestionForm()
    questionnaire = Questionnaire.select_all_questionnaires()

    if request.method == 'POST':
        if form.validate_on_submit():
            # add question to db and display question page
            Question.create_question(form.question_text.data, form.qstnnr_id.data)
            return redirect(url_for('question'))

    # display add-question form
    return render_template('add-question.html', categories=questionnaire, form=form)
# --------- end Questions ---------


# --------- EntityTag ---------
# display all entity-tags
@app.route('/entity-tag')
def entity_tag():
    entity_tags = EntityTags.select_all_entitytag()
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

            # adding entity to wit.ai
            client = WitClient(CONFIG['WIT_BASE_TOKEN'])
            client.create_entity(tag)
            st_code = client.create_sample(tag, expressions)
            if(st_code == 200):
                EntityTags.create_entitytag(form.tag_value.data, form.expressions.data)
            else:
                form._errors['Server error'] = 'Failed to push sample to wit.ai'
                return render_template('add-entitytag.html', form=form)
            # add question to db and display success page
            return redirect(url_for('entity_tag'))

    # display add-question form
    return render_template('add-entity-tag.html', form=form)
# --------- end EntityTag ---------


# --------- Info ---------
# display all info
@app.route('/info')
def info():
    all_info = Info.select_all_info()
    return render_template('info.html', info=all_info)


# add new info
@app.route('/add-info', methods=['POST', 'GET'])
def add_info():
    form = InfoForm()
    entity_tags = EntityTags.select_all_entitytag()
    if request.method == 'POST':
        if form.validate_on_submit():
            # adding info to db
            Info.create_info(form.tag_id.data, form.info_text.data)
            return redirect(url_for('info'))

    # display add-info form
    return render_template('add-info.html', form=form, etgs=entity_tags)
# --------- end Info ---------


# --------- Questionnaire ---------
# display all questionnaires
@app.route('/questionnaire')
def questionnaire():
    return render_template('questionnaire.html',
                           qstnnrs=Questionnaire.select_all_questionnaires())


# add new questionnaire
@app.route('/add-questionnaire', methods=['POST', 'GET'])
def add_questionnaire():
    form = QuestionnaireForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            # adding info to db
            Questionnaire.create_questionnaire(form.title.data, form.tag_id.data)
            return redirect(url_for('questionnaire'))

    # display add-question form
    return render_template('add-questionnaire.html', form=form,
                           et=EntityTags.select_all_entitytag())


# trigger sending questionnaire to all users of active event
@app.route('/send-questionnaire/<int:qstnnr_id>', methods=['POST'])
def send_questionnaire(qstnnr_id):
    # selecting targeted questionnaire
    qstnnr = Questionnaire.select_all_questions()
    
    # Trigger bot
    bot_launch_questionnaire_all_participants(qstnnr)

    # all the questions are here: questions = qstnnr.questions
    return redirect(url_for('questionnaire'))
# --------- end Questionnaire ---------


# --------- Feedback ---------
# displaying all feedback
@app.route('/feedback', methods=['GET'])
def feedback():
    fbk = Feedback.select_all_feedback()
    return render_template('feedback.html', feedback=fbk)
# --------- end Feedback ---------


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
    app.run(host='127.0.0.1', port=5001, debug=True, threaded=True)
