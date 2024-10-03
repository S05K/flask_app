from . import db
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy import PickleType



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
    is_admin = db.Column(db.Boolean, default=False)

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
        highest_score = db.Column(db.Integer, nullable=True)
        highest_wicket = db.Column(db.Float, nullable=True)
        total_innings = db.Column(db.Integer, nullable=True)
        strike_rate = db.Column(db.Integer, nullable=True)
        not_out = db.Column(db.Integer, nullable=True)
        price = db.Column(db.Integer, nullable=True)
        sold_price = db.Column(db.Integer, nullable=True)
        is_sold = db.Column(db.Boolean, default=False)

        user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
        user = db.relationship('User',back_populates='player_detail', uselist=False)

        def calculate_price(self):
                highest_score = self.highest_score or 0
                strike_rate = self.strike_rate or 0
                total_innings = self.total_innings or 0
                highest_wicket = self.highest_wicket or 0
                not_out = self.not_out or 0

                self.price =  (highest_score * 100) + (strike_rate * 100) + (total_innings * 100) + (highest_wicket * 100) + (not_out * 100)
                if self.price!=0:
                    return self.price
                else:
                    return self.price + 3000


        def to_dict(self):
            return {
                'id': self.id,
                'skill': self.skill,
                'price':self.price,
                'highest_score': self.highest_score,
                'highest_wicket': self.highest_wicket,
                'total_innings': self.total_innings,
                'strike_rate': self.strike_rate,
                'not_out': self.not_out,
                'sold_price' : self.sold_price,
                'user_id': self.user_id,
                'is_sold': self.is_sold,
                'user': self.user.to_dict()
            }

        

class OwnerDetail(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        money = db.Column(db.Integer)
        player_ids = db.Column(MutableList.as_mutable(PickleType), default=[])
        team_name = db.Column(db.String(80))

        user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
        user = db.relationship('User',back_populates='owner_detail', uselist=False)


