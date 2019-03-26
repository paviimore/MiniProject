from flask import Flask, render_template, request, jsonify
import plotly.graph_objs as go
from plotly.utils import PlotlyJSONEncoder
import json
import requests
import requests_cache
from cassandra.cluster import Cluster
import uuid
from flask import Flask
from flask.ext.cqlalchemy import CQLAlchemy

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('config.py')

app.config['CASSANDRA_HOSTS'] = ['127.0.0.1']
app.config['CASSANDRA_KEYSPACE'] = "cqlengine"
db = CQLAlchemy(app)

class Forex(db.Model):
    Country = db.columns.Text(required=False)
    Country_code = db.columns.Text(required=False)
    Currency = db.columns.Text(required=False)
    Currency_code = db.columns.Text(required=False)


requests_cache.install_cache('exchange_api_cache', backend='sqlite', expire_after=36000)

market_url= 'https://forex.1forge.com/1.0.3/market_status?api_key={key}'
forex_url= 'https://forex.1forge.com/1.0.3/quotes?pairs={pairs}&api_key={key}'
convert_url = 'https://forex.1forge.com/1.0.3/convert?from={fromCurrency}&to={toCurrency}&quantity={qty}&api_key={key}'
my_key = 'fCDpGAWjek59ZneVAawGJNbSRSWP6bD2'

@app.route('/marketstatus',  methods=['GET'])
def market():
    url = market_url.format(key=my_key)
    print(url)
    resp = requests.get(url)
    if resp.ok:
        response= resp.json()
        return jsonify(response)
    else:
        return (resp.reason)

@app.route('/exchangerate',  methods=['GET'])
def forexexchange():
    pairs = request.args.get('pairs')
    url = forex_url.format(pairs= pairs, key=my_key)
    print(url)
    resp = requests.get(url)
    if resp.ok:
        response= resp.json()
        return jsonify(response)
    else:
        return (resp.reason)

@app.route('/convert', methods=['GET'])
def convert():
    fromCurrency = request.args.get('from')
    toCurrency = request.args.get('to')
    qty = request.args.get('qty')

    url = convert_url.format(
        fromCurrency=fromCurrency, toCurrency=toCurrency, qty=qty, key=my_key)
    print(url)
    resp = requests.get(url)
    if resp.ok:
        response = resp.json()
        return jsonify(response)
    else:
        return (resp.reason)


@app.route('/entryCode', methods=['POST'])
def entry_code():
    ''' create or add new code '''
    data = request.get_json()
    if data['ok']:
        data = data['data']
        person = Forex(Country= data['Country'], Country_code= data['Country_code'],
                    Currency= data['Currency'], Currency_code= data['Currency_code'])
        person.save()
        return jsonify({'ok': True, 'data': data, 'message': 'Country code added successfully!'}), 200

    else:
        return jsonify({'ok': False, 'message': 'Bad request parameters: {}'.format(data['message'])}), 400


@app.route('/code', methods=['GET', 'DELETE'])
def code():
    ''' route read user '''
    if request.method == 'GET':
        query = request.args
        data = Forex.get('Country'= query['Country'])
        if bool(data):
            user = {}
            user['Country'] = data['Country']
            user['Code'] = data['Code']

            return jsonify({'ok': True, 'data': user}), 200
        else:
            return jsonify({'ok': False, 'message': 'No user exist with this mail'}), 400

    data = request.get_json()
    if request.method == 'DELETE':
             query = Forex.get('Country'= data['Country'])
            if bool(query):
                db_response = Forex.delete('Country' = data['Country']
                response = {'ok': True, 'message': 'record deleted'}
            else:
                response = {'ok': True, 'message': 'no record found'}
            return jsonify(response), 200
        else:
            return jsonify({'ok': False, 'message': 'Bad request parameters!'}), 400


if __name__=="__main__":
    app.run(port=8080, debug=True)
