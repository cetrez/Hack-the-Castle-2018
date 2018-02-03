from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired


class EntityTagForm(Form):
    tag_value = StringField('TagValue', validators=[DataRequired()])
    expressions = StringField('Expressions', validators=[DataRequired()])