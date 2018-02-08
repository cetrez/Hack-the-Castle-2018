from flask_wtf import Form
from wtforms import StringField, IntegerField
from wtforms.validators import DataRequired


class EntityTagForm(Form):
    tag_value = StringField('TagValue', validators=[DataRequired()])
    expressions = StringField('Expressions', validators=[DataRequired()])


class InfoForm(Form):
    cat_id = IntegerField('Category', validators=[DataRequired()])
    question_text = StringField('Text', validators=[DataRequired()])


class QuestionForm(Form):
    cat_id = IntegerField('Category', validators=[DataRequired()])
    question_text = StringField('Text', validators=[DataRequired()])