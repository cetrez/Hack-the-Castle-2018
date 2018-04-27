# Agent Smith - A manager bot
Project aims to create a chatbot which will make life easy for both participants and organizers
of events. Bot should be able to give user requested information, gather feedback, send notifications
from organizers and whatever devs can imagine!

## Background
Project was brainstormed during HackTheCastle at Cetrez and continued afterwards.

## Team
TeamSmith
- Oleksii Prykhodko
- Gunnar Stenlund
- Mohamed Hassainia
- Tulga Ariuntuya

## Setup instructions

```bash
git clone https://github.com/Dierme/Hack-the-Castle-2018 .
pip install -r requirments.txt
python flask_app.py
```
Then add a config.py to root of following structure
```code
CONFIG = {
    'FACEBOOK_TOKEN': '$token',
    'VERIFY_TOKEN': '$token',       #can be anything
    'SERVER_URL': '$Your server Url of the project',
    'SECRET_KEY': "$key",           #can be anything
    'WTF_CSRF_SECRET_KEY': "$key",  #can be anything
    'WIT_BASE_TOKEN': '$Wit base token',
    'AUTH_CODE': '$code'             #can be anything
}
```

Then visit [http://127.0.0.1:5000](http://127.0.0.1:5000)


## Demo
Admin panel of the bot.
[https://dierme.pythonanywhere.com/](https://dierme.pythonanywhere.com/)

Bot url on FB:
[https://www.facebook.com/Bot-1650634031646276/](https://www.facebook.com/Bot-1650634031646276/)
Chatting with bot in real time requires dev access as app is in development on fb

 
 