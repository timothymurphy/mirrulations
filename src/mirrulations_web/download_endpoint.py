from flask import Flask, request

FLASK_APP = Flask(__name__)


@FLASK_APP.route('/download', methods=['GET'])
def download():
	docid = request.args.get('docid')
