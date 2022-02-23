from flask.views import MethodView
from wtforms import Form, StringField, SubmitField
from flask import Flask, render_template,request
import boto3
import csv
import io
import gzip
from datetime import datetime

current_ts = datetime.now().strftime("%Y_%m_%d_%H_%M_%S_")

app = Flask(__name__)

# create S3 client
s3 = boto3.client('s3')

# bucket name
bucket_name = 'clauro-website-1'

mem_file = io.BytesIO()

class HomePage(MethodView):

    def get(self):
        return render_template('index.html')

class RestaurantFormPage(MethodView):

    def get(self):
        form = RestaurantForm()
        return render_template('forms.html', form = form)

class ResultsPage(MethodView):
    def post(self):
        form = RestaurantForm(request.form)
        cnpj = form.cnpj.data
        ownerName = form.ownerName.data

        with gzip.GzipFile(fileobj=mem_file, mode='wb', compresslevel=6) as gz:
            buff = io.StringIO()
            writer = csv.writer(buff)
            writer.writerows([(ownerName,cnpj)])
            gz.write(buff.getvalue().encode('utf-8', 'replace'))
        mem_file.seek(0)
        s3.put_object(Bucket=bucket_name, Key="data/"+ current_ts +"form_response.gz", Body=mem_file)
        return "Dados enviados com sucesso!" + "Obrigado, "+ ownerName + " por confiar na gente!"

class RestaurantForm(Form):
    restName = StringField("Nome do Restaurante: ")
    cnpj = StringField("CNPJ do Restaurante: ")
    ownerName = StringField("Nome do proprietário: ")
    ownerPhone = StringField("Número de Contato: ")

    button = SubmitField("Enviar")

app.add_url_rule('/', view_func=HomePage.as_view('home_page'))
app.add_url_rule('/forms', view_func=RestaurantFormPage.as_view('forms'))
app.add_url_rule('/results', view_func=ResultsPage.as_view('results'))


app.run()