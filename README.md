# Currency Exchange FOREX Web App

ECS781P – Cloud Computing Mini Project

A currency exchange app which retrieves the market status, exchange rates for a specific pair of currencies from an external API and also converts any given amount for a specific pair.
The app also has an internal API which links to a database of Countries with their corresponding codes, currencies & currency codes where you have the ability to view, add and delete existing entries from the database through the app. Information is returned in a JSON format.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.



The requirements file contains all the modules needed for the app.

### Installing

A step by step series of examples that tell you how to get a development env running

Download the project: git clone https://github.com/paviimore/MiniProject.git

Open command line and navigate to the directory of the folder where the app is stored.

Create a virtual environment with your preferred name with the following command.

```
python3 -m venv name_of_project
source name_of_project/bin/activate
```
The virtual environment needs to be activated with this command:
```
source name_of_project/bin/activate
```

From the app directory, run the following command:

```
python -m pip install -U -r requirements.txt
```
This command recursively installs/updates the modules in the requirement.txt in the local environment.

**Ensure these lines are removed from app.py:**
```
cluster = Cluster(['cassandra'])
session = cluster.connect()
db = CQLAlchemy(app)
class Exchange(db.Model):
    country = db.columns.Text(required=False, primary_key = True)
    countrycode = db.columns.Text(required=False)
    currency = db.columns.Text(required=False)
    code = db.columns.Text(required=False)
db.sync_db()
```

You should now be able run the app:

```
python app.py
```

This is successful if the terminal is displaying the following:

```
* Running on http://localhost:8080/ (Press CTRL+C to quit)
* Restarting with stat
* Debugger is active!
```
Clicking on the link should take you to the website.

## API

* GET 
``` 
/marketstatus 
/exchangerate?pairs="GivenPair"
/convert?from="InputCurrency"&to="OutputCurrency"&qty="quantity"
/code?country="CountryInDatabase"
```
* POST 
```
/entryCode?country="data1"&countrycode="data2"&currency="data3"&code="data4"
```
* DELETE 
```
/code?country="CountryInDatabase"
```

## Deployment

You will need the following before continuing:

* Docker
* Kubernetes

Setting configurations and creating clusters
```
export PROJECT_ID="$(gcloud config get-value project -q)"
gcloud config set project $PROJECT_ID
gcloud config set compute/zone us-central1-b
gcloud container clusters create cassandra --num-nodes=3 --machine-type "n1-standard-2"
```
Creating Replication Controllers for cassandra
```
wget -O cassandra-peer-service.yml http://tinyurl.com/yyxnephy
wget -O cassandra-service.yml http://tinyurl.com/y65czz8e
wget -O cassandra-replication-controller.yml http://tinyurl.com/y2crfsl8

kubectl create -f cassandra-peer-service.yml
kubectl create -f cassandra-service.yml
kubectl create -f cassandra-replication-controller.yml

kubectl scale rc cassandra --replicas=3
```
Creating keyspace and importing data from csv file
```
CREATE KEYSPACE forex WITH REPLICATION = {'class' : 'SimpleStrategy', 'replication_factor' : 2};
CREATE TABLE forex.exchange (country text PRIMARY KEY, countrycode text, currency text, code text);
COPY forex.exchange(country, countrycode, currency, code) FROM 'countrycodes.csv' WITH DELIMITER=',' AND HEADER=TRUE;
```

This section will detail how to get this app ready for a cloud environment. For example, Google Cloud
Once the directory is uploaded, run the docker build command in the directory of the app:

```
docker build -t gcr.io/${PROJECT_ID}/forex-app:v1 .
```
Once built, It will need to be pushed:
```
docker push gcr.io/${PROJECT_ID}/forex-app:v1
```
After being pushed, creating Kubernetes deployment from docker image and exposing port:
```
kubectl run forex-app --image=gcr.io/${PROJECT_ID}/forex-app:v1 --port 8080

kubectl expose deployment forex-app --type=LoadBalancer --port 80 --target-port 8080
```
Check services for the IP address: 
```
kubectl get services
```

## Built With

* [Cassandra](http://cassandra.apache.org/doc/latest/) - Database used
* [Flask](http://flask.pocoo.org/docs/1.0/) - Web framework used
* [1Forge](https://1forge.com/forex-data-api) - External API used
* [Kubernetes](https://kubernetes.io/docs/tasks/access-application-cluster/create-external-load-balancer/) - Load balancing & Scaling
* [Encryption & Security](https://blog.miguelgrinberg.com/post/running-your-flask-application-over-https) - TLS protocol using 'adhoc' SSL

## Authors

* **Pavitra Singh** - [Pavitra]( https://github.com/paviimore/MiniProject)
