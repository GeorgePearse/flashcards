
from flask import Flask, request, jsonify, render_template, url_for, redirect
import json
import requests
import pymongo
import json

client = pymongo.MongoClient("mongodb://localhost:27017/")
coll = client["local"]["test4"]


# %%
class card_set:
    def __init__(self,pairings,alternatives):
        self.pairings = pairings
        self.alternatives = alternatives

french = card_set({'bonjour':'hello'},{'bonjour':'salut'})

app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
def home():
    return render_template('temp_home.html')

@app.route('/insert', methods=['GET','POST'])
def insert():
    if request.method == 'GET':
        return render_template('form.html',user="George")
    if request.method == 'POST':
        text = request.form['text']
        key,value = text.split('=')
        coll.insert_one({key:value})
        return render_template('insert_response.html',key=key,value=value)
        
@app.route('/check', methods=['GET','POST'])
def check():
    if request.method == 'POST':
        text = request.form['text']
        collection = client["local"]["test4"].find_one({})

        dict_response = {} # this is a horrible temporary workaround!!!
        cursor = coll.find()
        for record in cursor:
            item = list(record.values())[1]
            value = list(record.keys())[1]
            if item not in list(record.keys()):
                dict_response[item] = value
            else:
                pass

        result = dict_response.get(text, 'item not in database')
        if result != 'item not in database':
            result += '     Selected card is in the deck'
        return render_template('check_response.html',check=str(text),result=str(result))

app.run(debug=True)

# %%