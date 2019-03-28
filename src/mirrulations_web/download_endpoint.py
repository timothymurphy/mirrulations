from io import BytesIO
from flask import Flask, send_file
from flask import request, render_template
import zipfile
import mirrulations_web.download_processor as download_processor

app = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':  # this block is only entered when the form is submitted
        mf=BytesIO();
        docid = request.form.get('DirId')

        print(docid)
        ZIP = zipfile.ZipFile(download_processor.download_zip(docid))
        mf.seek(0)
        print(ZIP)
        return send_file(mf, attachment_filename=docid + '.zip', as_attachment=True)
    return render_template("index.html")


if __name__ == "__main__":
    app.run()
