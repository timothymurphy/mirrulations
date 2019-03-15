import os
import mirrulations_web.download_processor as dp

REGULATIONS_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../test_files/regulations-data/")
AHRQ_PATH = "AHRQ_FRDOC/AHRQ_FRDOC_0001/AHRQ_FRDOC_0001-0036"


def test_download_zip():
    path = dp.download_zip('AHRQ_FRDOC_0001-0036', REGULATIONS_PATH+AHRQ_PATH)
    assert os.path.exists(path)
    os.remove(path)
