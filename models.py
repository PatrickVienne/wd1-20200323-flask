import os
from sqla_wrapper import SQLAlchemy

#db = SQLAlchemy(os.getenv("DATABASE_URL", "postgres://zubkimxqawbbud:b66c2693669d89633f65a355a0af1b29595a3634c4ac96c534df6f86f2410c6e@ec2-54-247-89-181.eu-west-1.compute.amazonaws.com:5432/dejr4kmdk15a8v"))
db = SQLAlchemy(os.getenv("DATABASE_URL", "sqlite:///C:\\smartninja\\wd1-20200323-flask\\localhost.sqlite"))


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    secret_number = db.Column(db.Integer, nullable=True)
    password = db.Column(db.String, nullable=True)
    login_token = db.Column(db.String, nullable=True)


class SecretNumberStore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cookie_identifier = db.Column(db.String, unique=True, nullable=False)
    secret_number = db.Column(db.Integer, nullable=False)
