import dill
import pandas as pd
import os

dill._dill._reverse_typemap['ClassType'] = type
# import cloudpickle
import flask
import logging
from logging.handlers import RotatingFileHandler
from time import strftime

# initialize our Flask application and the model
app = flask.Flask(__name__)
model = None

handler = RotatingFileHandler(filename='../app.log', maxBytes=100000, backupCount=10)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(handler)


def load_model(model_path):
    # load the pre-trained model
    global model
    with open(model_path, 'rb') as f:
        model = dill.load(f)
    print(model)


modelpath = "./models/pulsar_model.dill"
load_model(modelpath)


@app.route("/", methods=["GET"])
def general():
    return """Welcome to pulsar prediction process. Please use 'http://<address>/predict' to POST"""


@app.route("/predict", methods=["POST"])
def predict():
    # initialize the data dictionary that will be returned from the
    # view
    data = {"success": False}
    dt = strftime("[%Y-%b-%d %H:%M:%S]")
    # 	# ensure an image was properly uploaded to our endpoint
    if flask.request.method == "POST":
        Excess_kurtosis_of_the_integrated_profile = ''
        Skewness_of_the_integrated_profile = ''
        Mean_of_the_integrated_profile = ''
        request_json = flask.request.get_json()

        if request_json["Excess kurtosis of the integrated profile"]:
            Excess_kurtosis_of_the_integrated_profile = request_json['Excess kurtosis of the integrated profile']

        if request_json["Skewness of the integrated profile"]:
            Skewness_of_the_integrated_profile = request_json['Skewness of the integrated profile']

        if request_json["Mean of the integrated profile"]:
            Mean_of_the_integrated_profile = request_json['Mean of the integrated profile']

        logger.info(f'{dt} Data: Excess kurtosis of the integrated profile={Excess_kurtosis_of_the_integrated_profile},'
                    f'Skewness of the integrated profile={Skewness_of_the_integrated_profile},'
                    f'Mean of the integrated profile={Mean_of_the_integrated_profile}')
        try:
            preds = model.predict_proba(
                pd.DataFrame({"Excess kurtosis of the integrated profile": [Excess_kurtosis_of_the_integrated_profile],
                              "Skewness of the integrated profile": [Skewness_of_the_integrated_profile],
                              "Mean of the integrated profile": [Mean_of_the_integrated_profile]}))

        except AttributeError as e:
            logger.warning(f'{dt} Exception: {str(e)}')
            data['predictions'] = str(e)
            data['success'] = False
            return flask.jsonify(data)

        data["predictions"] = str(preds[:, 1][0])
        # indicate that the request was a success
        data["success"] = True

    # return the data dictionary as a JSON response
    return flask.jsonify(data)


# if this is the main thread of execution first load the model and
# then start the server
if __name__ == "__main__":
    print(("* Loading the model and Flask starting server..."
           "please wait until server has fully started"))
    port = int(os.environ.get('PORT', 8180))
    app.run(debug=True, port=port)
