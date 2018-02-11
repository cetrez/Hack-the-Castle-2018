# coding: utf-8
import os
import time
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir)

import json
from config import CONFIG
from fbmq import Attachment, Template, QuickReply, NotificationType
from fbpage import page
from flask import g
import models
from models.all_models import *

USER_SEQ = {}

CONFIDENCE_THRESHOLD = 0.8

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

    # Retrieve labels
    nlp = message['nlp']
    keyword = None
    confidence = 0

    # Turned off as nlp is behaving badly TODO
    '''
    if nlp is not None:
        items = nlp['entities'] #We're expecting only one item. Facebook dev settings, Built-In NLP
                                #However, seems I cant access item0, need to iterate through instead
        for ent_id in items:
            #ent_id is a string containing the entity id
            keyword = items[ent_id][0]['value']
            confidence = items[ent_id][0]['confidence']
    '''        
    print("Keyword = " + str(keyword) + ", Confidence = " + str(confidence))
    
    #TODO Dummy - used for testing bot capability to handle keywords from nlp.
    keyword = "Team"
    confidence = 1

    #TODO Not sure about the details
    seq_id = sender_id + ':' + recipient_id
    if USER_SEQ.get(seq_id, -1) >= seq:
        print("Ignore duplicated request")
        return None
    else:
        USER_SEQ[seq_id] = seq

    bot_receive(event, keyword, confidence)

@page.handle_delivery
def received_delivery_confirmation(event):
    delivery = event.delivery
    message_ids = delivery.get("mids")
    watermark = delivery.get("watermark")

    if message_ids:
        for message_id in message_ids:
            print("Received delivery confirmation for message ID: %s" % message_id)

    print("All message before %s were delivered." % watermark)


@page.handle_postback
def received_postback(event):
    sender_id = event.sender_id
    recipient_id = event.recipient_id
    time_of_postback = event.timestamp

    payload = event.postback_payload

    print("Received postback for user %s and page %s with payload '%s' at %s"
          % (sender_id, recipient_id, payload, time_of_postback))

    page.send(sender_id, "Postback called")


@page.handle_read
def received_message_read(event):
    watermark = event.read.get("watermark")
    seq = event.read.get("seq")

    print("Received message read event for watermark %s and sequence number %s" % (watermark, seq))


@page.handle_account_linking
def received_account_link(event):
    sender_id = event.sender_id
    status = event.account_linking.get("status")
    auth_code = event.account_linking.get("authorization_code")

    print("Received account link event with for user %s with status %s and auth code %s "
          % (sender_id, status, auth_code))


def send_message(recipient_id, text):
    # If we receive a text message, check to see if it matches any special
    # keywords and send back the corresponding example. Otherwise, just echo
    # the text we received.
    special_keywords = {
        "image": send_image,
        "gif": send_gif,
        "audio": send_audio,
        "video": send_video,
        "file": send_file,
        "button": send_button,
        "generic": send_generic,
        "receipt": send_receipt,
        "quick reply": send_quick_reply,
        "read receipt": send_read_receipt,
        "typing on": send_typing_on,
        "typing off": send_typing_off,
        "account linking": send_account_linking
    }

    if text in special_keywords:
        special_keywords[text](recipient_id)
    else:
        page.send(recipient_id, text, callback=send_text_callback, notification_type=NotificationType.REGULAR)


def send_text_callback(payload, response):
    print("SEND CALLBACK")


def send_image(recipient):
    page.send(recipient, Attachment.Image(CONFIG['SERVER_URL'] + "/assets/rift.png"))


def send_gif(recipient):
    page.send(recipient, Attachment.Image(CONFIG['SERVER_URL'] + "/assets/instagram_logo.gif"))


def send_audio(recipient):
    page.send(recipient, Attachment.Audio(CONFIG['SERVER_URL'] + "/assets/sample.mp3"))


def send_video(recipient):
    page.send(recipient, Attachment.Video(CONFIG['SERVER_URL'] + "/assets/allofus480.mov"))


def send_file(recipient):
    page.send(recipient, Attachment.File(CONFIG['SERVER_URL'] + "/assets/test.txt"))


def send_button(recipient):
    """
    Shortcuts are supported
    page.send(recipient, Template.Buttons("hello", [
        {'type': 'web_url', 'title': 'Open Web URL', 'value': 'https://www.oculus.com/en-us/rift/'},
        {'type': 'postback', 'title': 'tigger Postback', 'value': 'DEVELOPED_DEFINED_PAYLOAD'},
        {'type': 'phone_number', 'title': 'Call Phone Number', 'value': '+16505551234'},
    ]))
    """
    page.send(recipient, Template.Buttons("hello", [
        Template.ButtonWeb("Open Web URL", "https://www.oculus.com/en-us/rift/"),
        Template.ButtonPostBack("trigger Postback", "DEVELOPED_DEFINED_PAYLOAD"),
        Template.ButtonPhoneNumber("Call Phone Number", "+16505551234")
    ]))


@page.callback(['DEVELOPED_DEFINED_PAYLOAD'])
def callback_clicked_button(payload, event):
    print(payload, event)


def send_generic(recipient):
    page.send(recipient, Template.Generic([
        Template.GenericElement("rift",
                                subtitle="Next-generation virtual reality",
                                item_url="https://www.oculus.com/en-us/rift/",
                                image_url=CONFIG['SERVER_URL'] + "/assets/rift.png",
                                buttons=[
                                    Template.ButtonWeb("Open Web URL", "https://www.oculus.com/en-us/rift/"),
                                    Template.ButtonPostBack("tigger Postback", "DEVELOPED_DEFINED_PAYLOAD"),
                                    Template.ButtonPhoneNumber("Call Phone Number", "+16505551234")
                                ]),
        Template.GenericElement("touch",
                                subtitle="Your Hands, Now in VR",
                                item_url="https://www.oculus.com/en-us/touch/",
                                image_url=CONFIG['SERVER_URL'] + "/assets/touch.png",
                                buttons=[
                                    {'type': 'web_url', 'title': 'Open Web URL',
                                     'value': 'https://www.oculus.com/en-us/rift/'},
                                    {'type': 'postback', 'title': 'tigger Postback',
                                     'value': 'DEVELOPED_DEFINED_PAYLOAD'},
                                    {'type': 'phone_number', 'title': 'Call Phone Number', 'value': '+16505551234'},
                                ])
    ]))


def send_receipt(recipient):
    receipt_id = "order1357"
    element = Template.ReceiptElement(title="Oculus Rift",
                                      subtitle="Includes: headset, sensor, remote",
                                      quantity=1,
                                      price=599.00,
                                      currency="USD",
                                      image_url=CONFIG['SERVER_URL'] + "/assets/riftsq.png"
                                      )

    address = Template.ReceiptAddress(street_1="1 Hacker Way",
                                      street_2="",
                                      city="Menlo Park",
                                      postal_code="94025",
                                      state="CA",
                                      country="US")

    summary = Template.ReceiptSummary(subtotal=698.99,
                                      shipping_cost=20.00,
                                      total_tax=57.67,
                                      total_cost=626.66)

    adjustment = Template.ReceiptAdjustment(name="New Customer Discount", amount=-50)

    page.send(recipient, Template.Receipt(recipient_name='Peter Chang',
                                          order_number=receipt_id,
                                          currency='USD',
                                          payment_method='Visa 1234',
                                          timestamp="1428444852",
                                          elements=[element],
                                          address=address,
                                          summary=summary,
                                          adjustments=[adjustment]))


def send_quick_reply(recipient):
    """
    shortcuts are supported
    page.send(recipient, "What's your favorite movie genre?",
                quick_replies=[{'title': 'Action', 'payload': 'PICK_ACTION'},
                               {'title': 'Comedy', 'payload': 'PICK_COMEDY'}, ],
                metadata="DEVELOPER_DEFINED_METADATA")
    """
    page.send(recipient, "What's your favorite movie genre?",
              quick_replies=[QuickReply(title="Action", payload="PICK_ACTION"),
                             QuickReply(title="Comedy", payload="PICK_COMEDY")],
              metadata="DEVELOPER_DEFINED_METADATA")


@page.callback(['PICK_ACTION'])
def callback_picked_genre(payload, event):
    print(payload, event)


def send_read_receipt(recipient):
    page.mark_seen(recipient)


def send_typing_on(recipient):
    page.typing_on(recipient)


def send_typing_off(recipient):
    page.typing_off(recipient)


def send_account_linking(recipient):
    page.send(recipient, Template.AccountLink(text="Welcome. Link your account.",
                                              account_link_url=CONFIG['SERVER_URL'] + "/authorize",
                                              account_unlink_button=True))


def send_text_message(recipient, text):
    page.send(recipient, text, metadata="DEVELOPER_DEFINED_METADATA")

def initiate_feedback():
    for p in models.select_participants():
        page.send(p.fb_id, "We would appreciate your feedback!",
                  quick_replies=[QuickReply(title="Okay", payload="PICK_OK"),
                                 QuickReply(title="I'm busy", payload="PICK_NO")],
                  metadata="DEVELOPER_DEFINED_METADATA")
                  
def bot_receive(event, keyword, confidence):
    #Put new participants in DB
    bot_log_participant(event.sender_id)
        
    #Determine state
    current_state = State.get_state(event.sender_id)
    if(current_state is None):
        #Check if keyword is available and confidence is high enough
        if(confidence < CONFIDENCE_THRESHOLD or keyword is None):
            page.send(event.sender_id, "I'm sorry, but I have failed to interpret you")
            return
        
        #Check if keyword should trigger questionnaire
        #TODO Not currently working
        #questionnaire = Questionnaire.get_questionnaire(keyword)
        #Ugly "workaround"
        questionnaire = None
        if keyword == "Team":
            questionnaire = "Something"
        
        
        if questionnaire is not None:
            #Questionnaire is found, set state to retrieve answers
            #TODO Questionnaire id currently hardcoded
            current_state = State.create_state(event.sender_id, 1)
            #TODO replace with filtering using helper function
            questions = Question.select_all_questions()
            
            #Get user confirmation that user is interested in questionnaire
            #Could be solved by using State 0 to trigger quick_reply and never increment from 0->1 unless callback is OK
            #First question in Questionnaire contains text question to ask for participation
            
            bot_ask_participation(event.sender_id, questions[0].question)
        else:
            #Info state
            info = Info.get_info(keyword)
            bot_reply_info(event, info, keyword)
    else:
        #State is not None
        #Current msg from user concidered as questionnaire answer
        #State contains info on last q asked
        
        #If State q_numb == 0, it should be handled by callback function
        if(current_state.q_numb == 0):
            return
        
        #retrieve relevant questions
        questions = Question.select_all_questions() #TODO filter on Questionnaire
        
        last_question_id = questions[current_state.q_numb].id
        
        #TODO Save answer to DB. Currently crashes DB
        answer = event.message.get("text")
        #Feedback.create_feedback(last_question_id, event.sender_id, answer)
        
        #Iterate state
        current_state = State.inc_state(event.sender_id)
        page.send(event.sender_id, "state incremented {}".format(current_state.q_numb)) #Debug TODO remove
        
        #Ask next question or thank user
        
        if(current_state.q_numb >= len(questions)):
            page.send(event.sender_id, "Thank you")
            page.send(event.sender_id, str(current_state.q_numb))
            State.delete_state(event.sender_id)
        else:
            page.send(event.sender_id, str(current_state.q_numb))
            page.send(event.sender_id, questions[current_state.q_numb].question)
        
                
        
def bot_log_participant(fb_id) :
    participant = Participant.get_participant(fb_id)
    if participant is None:
        profile = page.get_user_profile(fb_id)
        name = "{} {}".format(profile['first_name'], profile['last_name'])
        participant = Participant.create_participant(name, fb_id)

#Retrieve info from DB and pass when calling this function        
def bot_reply_info(event, info, keyword):
    fail_reply = "Sorry, I have no information about {}".format(keyword)
    if info is not None:
        page.send(event.sender_id, info.info_text)
    else:
        page.send(event.sender_id, fail_reply)
        
def bot_ask_participation(recipient, question):
    page.send(recipient, question,
              quick_replies=[QuickReply(title="OK", payload="PICK_OK"),
                             QuickReply(title="No thanks", payload="PICK_NO")],
              metadata="DEVELOPER_DEFINED_METADATA") #TODO could be used to keep track of what questionnaire should be launched


@page.callback(['PICK_OK'])
def bot_callback_OK(payload, event):
    #Participant have accepted answering questionnaire. This is the only place where it is OK to proceed from state 0 to 1
    #Ask first question
    
    current_state = State.get_state(event.sender_id)
    
    #Should not happen - State SHOULD be created at this point
    if current_state is None or current_state.q_numb != 0:
        print("Unexpected state in bot_callback_OK")
        return
    
    #TODO replace with filtering using helper function
    questions = Question.select_all_questions()
    
    #Iterate state
    current_state = State.inc_state(event.sender_id)
    
    page.send(event.sender_id, str(current_state.q_numb))
    page.send(event.sender_id, questions[current_state.q_numb].question)
    
@page.callback(['PICK_NO'])
def bot_callback_NO(payload, event):
    
    current_state = State.get_state(event.sender_id)
    
    #Should not happen - State SHOULD be created at this point
    if current_state is None or current_state.q_numb != 0:
        print("Unexpected state in bot_callback_NO")
        return
        
    State.delete_state(event.sender_id)
