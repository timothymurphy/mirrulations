from flask import Flask, request

app = Flask(__name__)


@app.route('/download',methods=['GET'])
def download():
	docid = request.args.get('docid')
