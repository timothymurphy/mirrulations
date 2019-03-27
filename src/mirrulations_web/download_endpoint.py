from flask import request

from mirrulations_web import FLASK_APP


@FLASK_APP.route('/download',methods=['GET'])
def download():
	docid = request.args.get('docid')
