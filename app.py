
from flask import Flask, request, jsonify, render_template, url_for, redirect
import json
import requests
import pymongo

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
        return render_template('response.html',key=key,value=value)


app.run(debug=True)

# %%