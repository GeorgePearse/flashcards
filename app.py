
from flask import Flask, request, jsonify, render_template, url_for, redirect, session,send_file
from io import BytesIO
import json
import requests
import pymongo
import json
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_dangerously_set_inner_html
import random
import pandas as pd
from datetime import datetime

class data_store:
    def __init__(self, value):
        self.value = value


client = pymongo.MongoClient("mongodb://localhost:27017/")
cards = client["local"]["cards2"]
guesses_data = client["local"]["guesses_data"]

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

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

def retention(r1,t_passed):
    r = r1*np.exp(-t_passed*(1/r1))
    return r

@app.route("/login", methods=['GET','POST'])
@app.route('/', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('pretty_page.html')
    if request.method == 'POST':
        return render_template('home.html')

# Return the html table 
@app.route("/display_guesses", methods = ['GET'])
def display_pandas():
    array = list(guesses_data.find())
    guesses_df = pd.DataFrame(array)
    return render_template('table.html', table=guesses_df.to_html(), set_= "guesses_data")

@app.route("/display_cards", methods = ['GET'])
def display_cards():
    array = list(cards.find())
    cards_df = pd.DataFrame(array)
    return render_template('table.html', table=cards_df.to_html(), set_= "cards2")

@app.route("/excel/<set_>/", methods = ['GET'])
def excel_guesses(set_):
    collection = client["local"][set_]
    array = list(collection.find())
    cards_df = pd.DataFrame(array)
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    cards_df.to_excel(writer, sheet_name='Sheet1')
    writer.save()
    writer.save()
    output.seek(0)
    return send_file(output, attachment_filename='output.xlsx', as_attachment=True)


@app.route("/home", methods=['GET','POST'])
def home():
    return render_template('home.html')

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
        return render_template('insert.html',user="George")
    if request.method == 'POST':
        data = request.data
        form = request.form.to_dict()
        front = form.get('card_front', 'no front') # not working! 
        back = form.get('card_back', 'no back') 
        cards.insert_one({'front':front,'back':back,'time':datetime.now()}) # this will fix your future visualisation problem!!!!
        return render_template('insert.html',user="George")

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

@app.route('/delete', methods=['GET'])
def delete():
    return 'Delete Stuff here'

@app.route('/check', methods=['GET','POST'])
def check():        # order by minimum number of answers for now
    deck = {}
    array = list(guesses_data.find())
    guesses_df = pd.DataFrame(array) 
    guesses_df['num_guesses'] = guesses_df.groupby('right_answer').count()
    sorted_guesses = guesses_df.sort_values('num_guesses',ascending=True)

    cursor = cards.find({})
    for record in cursor:
        item = record['back']
        value = record['front']
        deck[item] = value

    if request.method == 'GET':
        card = guesses_df['right_answer'][0]
        right_answer = deck[card]
        session['right_answer'] = right_answer
        return render_template('question.html', card=card)

    if request.method == 'POST':
        data = request.form
        answer = data['card_front']
        right_answer = session.get('right_answer','FAILURE')
        guesses_data.insert_one({'right_answer':right_answer,'answer':answer,'time':datetime.now()}) # again this wil fix many problems down the line!
        match = "True" if answer == right_answer else "False"
        return render_template('check.html',right_answer=right_answer, answer=answer,match=match)

app.run(debug=True)
