from app import db


class authorized_member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100))
    phone_number = db.Column(db.String(15))
    constituency = db.Column(db.String(100))
    ward = db.Column(db.String(100))
    password = db.Column(db.String(20))


class sub_member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100))
    phone_number = db.Column(db.String(15))
    constituency = db.Column(db.String(100))
    ward = db.Column(db.String(100))
    ward_position = db.Column(db.String(50))
    authorized_member_id = db.Column(db.Integer, db.ForeignKey('authorized_member.id'))
