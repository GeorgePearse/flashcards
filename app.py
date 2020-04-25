
from flask import Flask, request, jsonify, render_template, url_for, redirect
import json
import requests
import pymongo
import json
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_dangerously_set_inner_html
import random
from flask_table import Table, Col #This is a hard barrier, have to resolve this first before you get anywhere good
from jinja2 import Template
import pandas as pd

# Declare your table
class ItemTable(Table):
    name = Col('Name')
    description = Col('Description')

# Get some objects
class Item(object):
    def __init__(self, name, description):
        self.name = name
        self.description = description

items = [Item('Name1', 'Description1'),
         Item('Name2', 'Description2'),
         Item('Name3', 'Description3')]
# Or, equivalently, some dicts
items = [dict(name='Name1', description='Description1'),
         dict(name='Name2', description='Description2'),
         dict(name='Name3', description='Description3')]

client = pymongo.MongoClient("mongodb://localhost:27017/")
coll = client["local"]["test4"]

app = Flask(__name__)

app2 = dash.Dash(
    __name__,
    server=app,
    url_base_pathname='/dash/'
)

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

app2.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1(
        children='Hello Dash',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),
    
    dash_dangerously_set_inner_html.DangerouslySetInnerHTML('''
            <form>
            <input type="button" value="Go back!" onclick="history.back()">
            </form>
            <body style="background-color:rgb(22, 22, 22)"> </body>
    '''),

    html.Div(children='Dash: A web application framework for Python.', style={
        'textAlign': 'center',
        'color': colors['text']
    }),

    dcc.Graph(
        id='example-graph-2',
        figure={
            'data': [
                {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
                {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'},
            ],
            'layout': {
                'plot_bgcolor': colors['background'],
                'paper_bgcolor': colors['background'],
                'font': {
                    'color': colors['text']
                }
            }
        }
    )
])

@app.route("/login", methods=['GET','POST'])
@app.route('/', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('pretty_page.html')
    if request.method == 'POST':
        return render_template('home_page.html')

# Print the html table
@app.route(rule="/display_table", methods = ['GET'])
def display_table():
    #rows = list(coll.find()) 
    #rows = str(rows).split('}, {')    
    table = ItemTable(items)
    return render_template('table.html', table=table.__html__())

@app.route(rule="/display_pandas", methods = ['GET'])
def display_pandas():
    array = list(coll.find())
    pls = pd.DataFrame(array)
    return render_template('table.html', table=pls.to_html())

@app.route("/home", methods=['GET','POST'])
def home():
    return render_template('home_page.html')

@app.route('/about', methods=['GET','POST'])
def about():
    return render_template('about.html')  

@app.route('/test', methods=['GET','POST'])
def test():
    return render_template('test.html')  

@app.route('/canvas', methods=['GET','POST'])
def canvas():
    return render_template('canvas.html')    
        
@app.route('/insert', methods=['GET','POST']) #hit simultaneously by two queries
def insert():
    if request.method == 'GET':
        return render_template('insert2.html',user="George")
    if request.method == 'POST':
        # not working!
        data = request.data
        form = request.form.to_dict()
        front = form.get('card_front', 'no front') # not working! 
        back = form.get('card_back', 'no back') 
        coll.insert_one({'front':front,'back':back}) # this will fix your future visualisation problem!!!!
        return render_template('insert_response.html',front=front,back=back,data='DATA = ' + str(data),form= 'FORM =' + str(form))

@app.route('/translate', methods=['GET','POST'])
def translate():
    if request.method == 'POST':
        text = request.form['text']
        url = "https://systran-systran-platform-for-language-processing-v1.p.rapidapi.com/translation/text/translate"
        querystring = {"source":"en","target":"fr","input":str(text)}
        headers = {
            'x-rapidapi-host': "systran-systran-platform-for-language-processing-v1.p.rapidapi.com",
            'x-rapidapi-key': "5629c1bf3fmshe44ae221a90eb80p153099jsne58bc0254bd4"
            }
        response = requests.request("GET", url, headers=headers, params=querystring)
        return json.loads(response.text)['outputs'][0]['output']

@app.route('/all_cards', methods=['GET']) # Call this the card stack?
def all_cards():
    deck = {}
    cursor = coll.find({})
    for record in cursor:
        item = list(record.values())[1]
        value = list(record.keys())[1]
        if item not in list(record.keys()):
            deck[item] = value
        else:
            pass
    return str(deck)

@app.route('/guesses', methods=['GET']) # Call this the card stack? -- want many of these as well!
def guesses():
    guesses_data = client["local"]["guesses"]
    cursor = guesses_data.find({})
    records = []
    for record in cursor:
        records.append(record)
    return str(records)

@app.route('/check', methods=['GET','POST'])
def check():
    guesses_data = client["local"]["guesses"]
    deck = {}
    cursor = coll.find({})
    for record in cursor:
        item = list(record.values())[1]
        value = list(record.keys())[1]
        if item not in list(record.keys()):
            deck[item] = value
        else:
            pass

    cards = list(deck.keys())
    card = random.choice(cards)
    right_answer = deck[card]
    if request.method == 'GET':
        return render_template('check.html', card=card)
    if request.method == 'POST':
        data = request.form
        answer = data['card_front']
        guesses_data.insert_one({'right_answer':right_answer,'answer':answer})
        return render_template('check.html', card=card, right_answer=right_answer, answer=answer)


app.run(debug=True)
