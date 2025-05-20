from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# MongoDB Atlas Connection (replace with your credentials)
client = MongoClient("mongodb+srv://rohanpash:rohanpash@mongotrail.pdqctpg.mongodb.net/?retryWrites=true&w=majority")
db = client["anonymous"]  # Database name

# Collections
users_col = db["users"]
messages_col = db["messages"]

@app.route('/')
def home():
    return render_template("index.html")

# Register user
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    uid = data['uid']
    email = data['email']
    if not users_col.find_one({'uid': uid}):
        users_col.insert_one({'uid': uid, 'email': email})
    return jsonify({'message': 'User registered'}), 200

# Get all users except current
@app.route('/users', methods=['POST'])
def get_users():
    data = request.get_json()
    current_uid = data['uid']
    users = list(users_col.find({'uid': {'$ne': current_uid}}, {'_id': 0}))
    return jsonify(users)

# Store anonymous message with sender_uid
@app.route('/send', methods=['POST'])
def send_message():
    data = request.get_json()
    message = {
        'sender_uid': data['sender'],
        'receiver_uid': data['receiver'],
        'content': data['content'],
        'timestamp': datetime.utcnow()
    }
    messages_col.insert_one(message)
    return jsonify({'message': 'Message sent'}), 200

# Retrieve inbox (hide sender info)
@app.route('/inbox', methods=['POST'])
def inbox():
    data = request.get_json()
    uid = data['uid']
    msgs = messages_col.find({'receiver_uid': uid}).sort('timestamp', -1)
    result = []
    for msg in msgs:
        result.append({
            'from': 'Anonymous',  # Sender hidden from user
            'content': msg['content'],
            'timestamp': msg['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
        })
    return jsonify(result)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True)
