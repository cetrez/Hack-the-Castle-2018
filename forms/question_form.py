from flask_wtf import Form
from wtforms import SelectMultipleField, StringField, IntegerField
from wtforms.validators import DataRequired


class QuestionForm(Form):
    cat_id = IntegerField('Category', validators=[DataRequired()])
    question_text = StringField('Text', validators=[DataRequired()])