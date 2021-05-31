import json

from flask import Flask, render_template, redirect, url_for, request
from flask_wtf import FlaskForm
from requests.exceptions import ConnectionError
from wtforms import IntegerField, SelectField, StringField
from wtforms.validators import DataRequired

import urllib.request
import json


class ClientDataForm(FlaskForm):
    Excess_kurtosis_of_the_integrated_profile = StringField('Excess kurtosis of the integrated profile',
                                                            validators=[DataRequired()])
    Skewness_of_the_integrated_profile = StringField('Skewness of the integrated profile', validators=[DataRequired()])
    Mean_of_the_integrated_profile = StringField('Mean of the integrated profile', validators=[DataRequired()])


app = Flask(__name__)
app.config.update(
    CSRF_ENABLED=True,
    SECRET_KEY='you-will-never-guess',
)


def get_prediction(Excess_kurtosis_of_the_integrated_profile,
                   Skewness_of_the_integrated_profile,
                   Mean_of_the_integrated_profile):
    body = {'Excess kurtosis of the integrated profile': Excess_kurtosis_of_the_integrated_profile,
            'Skewness of the integrated profile': Skewness_of_the_integrated_profile,
            'Mean of the integrated profile': Mean_of_the_integrated_profile}

    myurl = "http://0.0.0.0:8180/predict"
    req = urllib.request.Request(myurl)
    req.add_header('Content-Type', 'application/json; charset=utf-8')
    jsondata = json.dumps(body)
    jsondataasbytes = jsondata.encode('utf-8')  # needs to be bytes
    req.add_header('Content-Length', len(jsondataasbytes))
    print(jsondataasbytes)
    response = urllib.request.urlopen(req, jsondataasbytes)
    return json.loads(response.read())['predictions']


@app.route("/")
def index():
    return render_template('index.html')


@app.route('/predicted/<response>')
def predicted(response):
    response = json.loads(response)
    print(response)
    return render_template('predicted.html', response=response)


@app.route('/predict_form', methods=['GET', 'POST'])
def predict_form():
    form = ClientDataForm()
    data = dict()
    if request.method == 'POST':
        data['Excess kurtosis of the integrated profile'] = request.form.get(
            'Excess_kurtosis_of_the_integrated_profile')
        data['Skewness of the integrated profile'] = request.form.get('Skewness_of_the_integrated_profile')
        data['Mean of the integrated profile'] = request.form.get('Mean_of_the_integrated_profile')

        try:
            response = str(get_prediction(data['Excess kurtosis of the integrated profile'],
                                          data['Skewness of the integrated profile'],
                                          data['Mean of the integrated profile']))
            print(response)
        except ConnectionError:
            response = json.dumps({"error": "ConnectionError"})
        return redirect(url_for('predicted', response=response))
    return render_template('form.html', form=form)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8181, debug=True)
