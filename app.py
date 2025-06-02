# To run this code you need to install the following dependencies:
# pip install google-genai

import base64
import os
from flask import Flask, request as req, jsonify, render_template, redirect, url_for
import google.generativeai as genai
# from google.genai import types
from dotenv import load_dotenv
# from google import genai
from pymongo import MongoClient

load_dotenv()

genai.configure(api_key = os.environ['GEMINI_API_KEY'])
model = genai.GenerativeModel("gemini-1.5-flash")

app = Flask(__name__)
app.debug = True 

mongo_client = MongoClient(os.environ['MONGO_URI'])
db =mongo_client['gemini_chat']
chat_collection = db['chats']

@app.route('/', methods=['GET', 'POST'])
def chat():
    if req.method == 'POST':
        room_id = req.form.get('room_id')
    else:
        room_id = req.args.get('room_id')

    chat_hist = []

    room_doc = None
    if room_id:
        room_doc = chat_collection.find_one({"room_id": room_id})
        if not room_doc:
            room_doc = {"room_id":room_id, "history": []}
        
        if req.method == 'POST':
            user_input = req.form['query']
            response = model.generate_content(user_input)
            response_text = response.text
            room_doc['history'].append({
                "user":user_input,
                "bot":response_text
            })
            chat_collection.update_one(
                {"room_id": room_id},
                {"$set": {"history": room_doc["history"]}},
                upsert=True
            )
            print(f"{room_doc}")
            return redirect(url_for('chat', room_id= room_id))
        chat_hist = room_doc.get("history", [])
    return render_template('index.html', chat_hist=chat_hist, room_id=room_id)


@app.route('/clear/<room_id>')
def clear_chat(room_id):
    chat_collection.delete_one({"room_id": room_id})
    return redirect(url_for('chat'))

if __name__ == "__main__":
    app.run(
        debug=True,
        use_reloader=True,
        use_debugger=True,
        host='127.0.0.1',
        port=5000
    )



