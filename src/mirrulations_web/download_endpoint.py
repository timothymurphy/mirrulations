from flask import Flask
from flask import request

app = Flask(__name__)


@app.route("/download", methods=['GET'])
def download():
    docid = request.args.get('docid')
