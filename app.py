from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from flask_cors import CORS

DATABASE_URL = 'postgres://lnxlvpzkblhmzv:24c911669b98a96ca53c5bb5fe4f278d0aa8bf687deba7b73a6ac8756271c044@ec2-54-147-107-18.compute-1.amazonaws.com:5432/d6716ebracrnpj'

app = Flask(__name__)

app.config['DATABASE_URL'] = DATABASE_URL
db = SQLAlchemy(app)
CORS(app)
migrate = Migrate(app, db)

class Users(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    image_url = db.Column(db.String(120))
    children = relationship("Groups")

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password

    def __repr__(self):
        return f"<User {self.name}"


class Groups(db.Model):
    __tablename__ = 'groups'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    code = db.Column(db.String(7), nullable=False)
    adminUser = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)

    def __init__(self, name, code, adminUser, user_id):
        self.name = name
        self.code = code
        self.adminUser = adminUser
        self.user_id = user_id

    def __repr__(self):
        return f"<Group {self.name}"


class Messages(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(5000), nullable=False)
    user_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)
    group_id = db.Column(db.String(7), nullable=False)


    def __init__(self, text, user_id, group_id):
        self.text = text
        self.user_id = user_id
        self.group_id = group_id

    def __repr__(self):
        return f"<Message {self.user_id}"


def init_db():
    db.create_all()

@app.route('/users', methods=['GET'])
def fetch_users():
    all_users = Users.query.all()
    results = [
        {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "password": user.password,
            "image_url": user.image_url
        } for user in all_users]

    return {"count": len(results), "users": results}

@app.route('/add_user', methods=['POST'])
def add_user():
    if request.is_json:
        data = request.get_json()
        new_user = Users(name=data['name'], email=data['email'], password=data['password'])
        db.session.add(new_user)
        db.session.commit()
        return {"message": f"user {new_user.name} has been created successfully."}
    else:
        return {"error": "The request payload is not in JSON format"}


@app.route('/users/<id>', methods=['GET'])
def fetch_user(id):
    user = Users.query.get_or_404(id)
    results = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "password": user.password,
            "image_url": user.image_url
        }

    return {"user": "success", "user": results}


@app.route('/edit_user/<user_id>', methods=['PUT'])
def edit_user(user_id):
        user = Users.query.get_or_404(user_id)
        data = request.get_json()
        user.image_url = data['image_url']
        db.session.add(user)
        db.session.commit()
        return {"message": "user image successfully updated"}


@app.route('/groups', methods=['GET'])
def fetch_groups():
    all_groups = Groups.query.all()
    results = [
        {
            "id": group.id,
            "name": group.name,
            "code": group.code,
            "adminUser": group.adminUser,
            "user_id": group.user_id
        } for group in all_groups]

    return {"count": len(results), "groups": results}


@app.route('/add_group', methods=['POST'])
def add_group():
    if request.is_json:
        data = request.get_json()
        new_group = Groups(name=data['name'], code=data['code'], adminUser=data['adminUser'], user_id=data['user_id'])
        db.session.add(new_group)
        db.session.commit()
        return {"message": f"group {new_group.name} has been created successfully."}
    else:
        return {"error": "The request payload is not in JSON format"}


@app.route('/groups/<group_id>', methods=['DELETE'])
def group(group_id):
    group = Groups.query.get_or_404(group_id)
    db.session.delete(group)
    db.session.commit()
    return {"group": f"Group {group.name} successfully deleted."}



@app.route('/messages', methods=['GET'])
def fetch_messages():
    all_messages = Messages.query.all()
    results = [
        {
            "id": message.id,
            "text": message.text,
            "user_id": message.user_id,
            "group_id": message.group_id
        } for message in all_messages]

    return {"count": len(results), "messages": results}

    
@app.route('/messages/<id>', methods=['GET'])
def fetch_message(id):
    message = Messages.query.get_or_404(id)
    results = {
            "id": message.id,
            "text": message.text,
            "user_id": message.user_id,
            "group_id": message.group_id
        }

    return {"message": "success", "message": results}


@app.route('/add_message', methods=['POST'])
def add_message():
    if request.is_json:
        data = request.get_json()
        new_message = Messages(text=data['text'], user_id=data['user_id'], group_id=data['group_id'])
        db.session.add(new_message)
        db.session.commit()
        return {"message": f"message from user {new_message.user_id} has been created successfully."}
    else:
        return {"error": "The request payload is not in JSON format"}


@app.route('/messages/<message_id>', methods=['DELETE'])
def message(message_id):
    message = Messages.query.get_or_404(message_id)
    db.session.delete(message)
    db.session.commit()
    return {"message": f"Message {message.user_id} successfully deleted."}

@app.route('/')
def hello():
    return "Chat App Capstone API Homepage"


if __name__ == '__main__':
    app.run(debug=True)
    init_db()