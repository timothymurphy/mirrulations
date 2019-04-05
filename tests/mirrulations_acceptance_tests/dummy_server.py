from flask import Flask

app = Flask(__name__)
version = 'v1.3'


@app.route('/')
def default():
    pass


@app.route('/get_work')
def get_work():
    pass


@app.route('/return_docs', methods=['POST'])
def return_docs():
    pass


@app.route('/return_doc', methods=['POST'])
def return_doc():
    pass


def run():
    app.run('0.0.0.0', '8080')


if __name__ == '__main__':
    run()
