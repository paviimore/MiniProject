from flask import Flask, render_template, request, jsonify
import plotly.graph_objs as go
from plotly.utils import PlotlyJSONEncoder
import json
import requests
import requests_cache
"""
from cassandra.cluster import Cluster

cluster = Cluster(['cassandra'])
session = cluster.connect()
app = Flask(__name__)
"""
requests_cache.install_cache('exchange_api_cache', backend='sqlite', expire_after=36000)

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('config.py')

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



if __name__=="__main__":
    app.run(port=8080, debug=True)
