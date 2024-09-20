from . import db


ROLE_CHOICES = {
    'owner': 'owner',
    'player': 'player'
    }

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=True, nullable=False)
    role = db.Column(db.String(10), nullable=False)
    
    player_detail = db.relationship('PlayerDetail', back_populates='user')
    owner_detail = db.relationship('OwnerDetail', back_populates='user')

    def __repr__(self):
        return f'<User {self.name}, Role: {self.role}>'

    def is_owner(self):
        return self.role == ROLE_CHOICES['owner']

    def is_player(self):
        return self.role == ROLE_CHOICES['player']

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email' : self.email,
            'role' : self.role
        }
    
class PlayerDetail(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        skill = db.Column(db.String(80))
        highest_score = db.Column(db.Float, nullable=True)
        highest_wicket = db.Column(db.Float, nullable=True)
        total_innings = db.Column(db.Integer, nullable=True)
        strike_rate = db.Column(db.Integer, nullable=True)
        not_out = db.Column(db.Integer, nullable=True)

        user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
        user = db.relationship('User',back_populates='player_detail', uselist=False)


class OwnerDetail(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        money = db.Column(db.Integer)

        user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
        user = db.relationship('User',back_populates='owner_detail', uselist=False)


