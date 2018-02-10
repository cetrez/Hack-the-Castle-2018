from flask_wtf import Form
from wtforms import StringField, IntegerField
from wtforms.validators import DataRequired


class EntityTagForm(Form):
    tag_value = StringField('TagValue', validators=[DataRequired()])
    expressions = StringField('Expressions', validators=[DataRequired()])


class InfoForm(Form):
    tag_id = IntegerField('Category', validators=[DataRequired()])
    info_text = StringField('Text', validators=[DataRequired()])


class QuestionForm(Form):
    qstnnr_id = IntegerField('Category', validators=[DataRequired()])
    question_text = StringField('Text', validators=[DataRequired()])


class QuestionnaireForm(Form):
    title = StringField('Title', validators=[DataRequired()])
    tag_id = IntegerField('Entity Tag', validators=[DataRequired()])