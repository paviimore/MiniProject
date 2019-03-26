from flask import Flask, render_template, request, jsonify
import json
import requests
import requests_cache
from cassandra.cluster import Cluster
import uuid
from flask_cqlalchemy import CQLAlchemy
from cassandra.cluster import Cluster
cluster = Cluster(['127.0.0.1'])
session = cluster.connect()
app = Flask(__name__)

app.config['CASSANDRA_HOSTS'] = ['Cassandra']
app.config['CASSANDRA_KEYSPACE'] = "forex"
db = CQLAlchemy(app)


class Exchange(db.Model):
    country = db.columns.Text(required=False, primary_key = True)
    countrycode = db.columns.Text(required=False)
    currency = db.columns.Text(required=False)
    code = db.columns.Text(required=False)
db.sync_db()


#Exchange.create(Country= 'Asgard', CountryCode= 'ASG', Currency= 'Gallions', Code = 'GLL')

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
    # create or add new code
    query = request.args
    rows = session.execute("""insert into forex.exchange (country, countrycode, currency, code) values('{}',
    '{}','{}','{}');""".format(query['country'], query['countrycode'], query['currency'], query['code']))

    #rows = session.execute("""insert into forex.exchange (country, countrycode, currency, code) values('Wakanda', 'Wak','Vibranium','vib');""")
    return jsonify({'ok': True, 'message': 'Country code added successfully!'}), 200



@app.route('/code', methods=['GET', 'DELETE'])
def code():
    ''' route read user '''
    if request.method == 'GET':
        query = request.args
        data = Exchange.get(country = query['country'])
        if bool(data):
            user = {}
            user['country'] = data['country']
            user['currency'] = data['currency']
            user['code'] = data['code']

            return jsonify({'ok': True, 'data': user}), 200
        else:
            return jsonify({'ok': False, 'message': 'No user exist with this mail'}), 400


    if request.method == 'DELETE':
        query = request.args
        rows = session.execute("""delete from forex.exchange where country = '{}';""".format(query['country']))
        return jsonify({'ok': True, 'message': 'Country data deleted successfully!'}), 200


if __name__ == "__main__":
    app.run(port=8080, debug=True)
