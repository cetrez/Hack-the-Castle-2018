# coding: utf-8
import os
import time
from fbmq import QuickReply, NotificationType
from fbpage import page
import models
from models.all_models import *

USER_SEQ = {}
CONFIDENCE_THRESHOLD = 0.5
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0, parentdir)


@page.handle_optin
def received_authentication(event):
    sender_id = event.sender_id
    recipient_id = event.recipient_id
    time_of_auth = event.timestamp

    pass_through_param = event.optin.get("ref")

    print("Received authentication for user %s and page %s with pass "
          "through param '%s' at %s" % (sender_id, recipient_id, pass_through_param, time_of_auth))

    page.send(sender_id, "Authentication successful")


@page.handle_echo
def received_echo(event):
    message = event.message
    message_id = message.get("mid")
    app_id = message.get("app_id")
    metadata = message.get("metadata")
    print("page id : %s , %s" % (page.page_id, page.page_name))
    print("Received echo for message %s and app %s with metadata %s" % (message_id, app_id, metadata))


def send_humanly(sender_id, text):
    send_typing_on(sender_id),
    time.sleep(len(text.split(' '))/5.0)
    send_message(sender_id, text)
    send_typing_off(sender_id)


@page.handle_message
def received_message(event):
    sender_id = event.sender_id
    recipient_id = event.recipient_id
    time_of_message = event.timestamp
    message = event.message
    print("Received message for user %s and page %s at %s with message:"
          % (sender_id, recipient_id, time_of_message))
    print(message)

    seq = message.get("seq", 0)
    message_id = message.get("mid")
    app_id = message.get("app_id")
    metadata = message.get("metadata")

    message_text = message.get("text")
    message_attachments = message.get("attachments")
    quick_reply = message.get("quick_reply")

    # Should NOT take care of callbacks TODO this might be a dirty solution
    if quick_reply is not None:
        print("received message contains payload, returning")
        return

    # Retrieve labels
    nlp = message['nlp']
    keyword = None
    confidence = 0

    # Get keywords from nlp
    if nlp is not None:
        # We're expecting only one item. Facebook dev settings, Built-In NLP
        # However, seems I cant access item0, need to iterate through instead
        items = nlp['entities']
        for ent_id in items:
            # ent_id is a string containing the entity id
            keyword = items[ent_id][0]['value']
            confidence = items[ent_id][0]['confidence']    

    print("Keyword = " + str(keyword) + ", Confidence = " + str(confidence))

    # TODO Not sure about the details. Avoids several handlings of the same event.
    seq_id = sender_id + ':' + recipient_id
    if USER_SEQ.get(seq_id, -1) >= seq:
        print("Ignore duplicated request")
        return None
    else:
        USER_SEQ[seq_id] = seq

    bot_receive(event, keyword, confidence)


def send_message(recipient_id, text):
        page.send(recipient_id, text,
                  callback=send_text_callback,
                  notification_type=NotificationType.REGULAR)


def send_text_callback(payload, response):
    print('Callback send')


def send_text_message(recipient, text):
    page.send(recipient, text, metadata="DEVELOPER_DEFINED_METADATA")


def initiate_feedback():
    for p in models.select_participants():
        page.send(p.fb_id, "We would appreciate your feedback!",
                  quick_replies=[QuickReply(title="Okay", payload="PICK_OK"),
                                 QuickReply(title="I'm busy", payload="PICK_NO")],
                  metadata="DEVELOPER_DEFINED_METADATA")


def bot_receive(event, keyword, confidence):
    # Put new participants in DB
    bot_log_participant(event.sender_id)

    # Determine state
    current_state = State.get_state(event.sender_id)
    print("current_state == None {}".format(current_state is None))
    if current_state is None:
        # Check if keyword is available and confidence is high enough
        if confidence < CONFIDENCE_THRESHOLD or keyword is None:
            page.send(event.sender_id, "I'm sorry, but I have failed to interpret you")
            return

        # Check if keyword should trigger questionnaire
        questionnaire = Questionnaire.get_questionnaire(keyword)

        if questionnaire is not None:
            # Questionnaire is found, set state and retrieve questions
            current_state = State.create_state(event.sender_id, questionnaire.id)
            print("State created, qnnr={}".format(current_state.q_numb))
            # questions = get_questions(current_state.qstnnr.id)

            # Get user confirmation that user is interested in questionnaire
            # Could be solved by using State 0 to trigger quick_reply and never increment
            #       from 0->1 unless callback is OK
            # First question in Questionnaire contains text question to ask for participation

            question = "Is it ok if I ask you a few questions about {}".format(questionnaire.title)
            bot_ask_participation(event.sender_id, question)
            # page.send(event.sender_id, questions[current_state.q_numb].question)

        else:
            #Info state
            info = Info.get_info(keyword)
            if info is not None:
                bot_reply_info(event, info, keyword)
            else:
                page.send(event.sender_id, "I'm sorry, but I have no information for you")
    else:
        # State is not None
        # Current msg from user concidered as questionnaire answer
        # State contains info on last q asked

        # If State q_numb == 0, it should be handled by callback function
        # Execution here could indicate a bug. Deleting state to avoid getting stuck
        # if current_state.q_numb == 0:
        #     State.delete_state(event.sender_id)
        #     return

        # retrieve relevant questions
        # questions = get_questions(current_state.qstnnr.id)
        questions = Questionnaire.select_all_questions(current_state.qstnnr.id)

        last_question_id = questions[current_state.q_numb].id

        # Save answer to DB.
        answer = event.message.get("text")
        Feedback.create_feedback(last_question_id, event.sender_id, answer)

        # Iterate state
        current_state = State.inc_state(event.sender_id)

        # Ask next question or thank user

        if current_state.q_numb >= len(questions):
            page.send(event.sender_id, "Thank you")
            State.delete_state(event.sender_id)
        else:
            page.send(event.sender_id, questions[current_state.q_numb].question)


def bot_log_participant(fb_id):
    participant = Participant.get_participant(fb_id)
    if participant is None:
        profile = page.get_user_profile(fb_id)
        name = "{} {}".format(profile['first_name'], profile['last_name'])
        participant = Participant.create_participant(name, fb_id)
    return participant


# Retrieve info from DB and pass when calling this function
def bot_reply_info(event, info, keyword):
    reply = "Sorry, I have no information about '{}'".format(keyword)
    if info is not None:
        reply = info.info_text
    page.send(event.sender_id, reply)


# TODO could be used to keep track of what questionnaire should be launched
def bot_ask_participation(recipient, question):
    page.send(recipient, question,
              quick_replies=[QuickReply(title="OK", payload="PICK_OK"),
                             QuickReply(title="No thanks", payload="PICK_NO")],
              metadata="DEVELOPER_DEFINED_METADATA")


@page.callback(['PICK_OK'])
def bot_callback_ok(payload, event):
    # Participant have accepted answering questionnaire.
    # This is the only place where it is OK to proceed from state 0 to 1
    # Ask first question

    current_state = State.get_state(event.sender_id)
    print("current_state == None {}".format(current_state is None))

    # Should not happen - State SHOULD be created at this point
    if current_state is None or current_state.q_numb != 0:
        print("Unexpected state in bot_callback_OK")
        print(str(event.sender_id))
        return

    # Get list of questions
    # questions = get_questions(current_state.qstnnr.id)
    questions = Questionnaire.select_all_questions(current_state.qstnnr.id)

    page.send(event.sender_id, questions[current_state.q_numb].question)


@page.callback(['PICK_NO'])
def bot_callback_no(payload, event):
    current_state = State.get_state(event.sender_id)

    # Should not happen - State SHOULD be created at this point
    if current_state is None or current_state.q_numb != 0:
        print("Unexpected state in bot_callback_NO")
        return
    State.delete_state(event.sender_id)
    text = "Ok, maybe next time! Have a good day!"
    page.send(event.sender_id, text)


# Returns a list of questions filtered on qnnr_id
# TODO consider placement of this function or implement DB get function
def get_questions(questionnaire_id):
    questions = Question.select_all_questions()
    qs = []
    for question in questions:
        if question.qtnnr.id == questionnaire_id:
            qs.append(question)
    return qs


def send_typing_off(recipient):
    page.typing_off(recipient)


def send_typing_on(recipient):
    page.typing_on(recipient)
    
# Launching questionnaire from web interface (organizer)
# Wont launch for participants already in questionnaire - states are not advanced enough to handle this.
def bot_launch_questionnaire_all_participants(questionnaire):
    for participant in Participant.select_all_participants():
        current_state = State.get_state(participant.fb_id)
        if current_state is None:
            #Launch questionnaire
            #Set state
            current_state = State.create_state(participant.fb_id, questionnaire.id)
            print("State created, qnnr={}".format(current_state.q_numb))
            #Ask participant
            question = "We would like to have your opinion on {}. Is it ok if I ask you a few questions?".format(questionnaire.title)
            bot_ask_participation(participant.fb_id, question)

# Arg String msg is message to all registered participants            
def bot_msg_all_participants(msg):
    for participant in Participant.select_all_participants():
        page.send(participant.fb_id, msg)
        
