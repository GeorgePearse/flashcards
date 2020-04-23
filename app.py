
from flask import Flask, request, jsonify, render_template, url_for, redirect
import json
import requests
import pymongo
import json
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_dangerously_set_inner_html


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

@app.route("/home", methods=['GET','POST'])
@app.route('/', methods=['GET','POST'])
def home():
    return render_template('pretty_page.html')

@app.route('/about', methods=['GET','POST'])
def about():
    return render_template('about.html')    

@app.route('/insert', methods=['GET','POST']) #hit simultaneously by two queries
def insert():
    if request.method == 'GET':
        return render_template('form.html',user="George")
    if request.method == 'POST':
        test = request.form
        #coll.insert_one({key:value})
        return test #render_template('insert_response.html',key=key,value=value)
        
@app.route('/ajax', methods=['GET','POST']) #hit simultaneously by two queries
def ajax():
    if request.method == 'GET':
        return render_template('ajax.html',user="George")
    if request.method == 'POST':
        front = request.form.get('cfront', 'no front')
        back = request.form.get('cback', 'no back')
        coll.insert_one({front:back})
        return render_template('insert_response.html',front = front, back = back)

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

@app.route('/check', methods=['GET','POST'])
def check():
    if request.method == 'POST':
        text = request.form['text']
        collection = client["local"]["test4"].find_one({})

        dict_response = {} # this is a horrible temporary workaround to convert mongodb output to a dictionary of pairs of words!!!
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
