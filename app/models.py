from app import db 

tags = db.Table('tags',
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True),
    db.Column('bookmark_id', db.Integer, db.ForeignKey('bookmark.id'), primary_key=True)
)

class Bookmark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String)
    title = db.Column(db.String)
    description = db.Column(db.Text)
    date = db.Column(db.DateTime)
    tags = db.relationship('Tag', secondary=tags, lazy='subquery',
        backref=db.backref('bookmarks', lazy=True))


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)



