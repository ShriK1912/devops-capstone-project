from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    phone = db.Column(db.String(32), nullable=False, default="")
    account_type = db.Column(db.String(50), nullable=False, default="personal")
    status = db.Column(db.String(20), nullable=False, default="active")
    balance = db.Column(db.Numeric(12, 2), nullable=False, default=0)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "account_type": self.account_type,
            "status": self.status,
            "balance": float(self.balance),
        }
