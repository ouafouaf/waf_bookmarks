from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, HiddenField
from wtforms.validators import DataRequired

class PostBookmarkForm(FlaskForm):
    url = StringField('URL', validators=[DataRequired()])
    title = StringField('Title')
    description = TextAreaField('Description')
    add = SubmitField('Add')

class EditBookmarkForm(FlaskForm):
    url = StringField('URL', validators=[DataRequired()])
    title = StringField('Title')
    description = TextAreaField('Description')
    myid = StringField('0')
    edit = SubmitField('Edit')

class DeleteBookmarkForm(FlaskForm):
    myid = StringField('0')
    delete = SubmitField('Delete')