import zipfile
import mirrulations_web.directory_zip as dz
import os
import shutil

PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../test_files/regulations-data/")
add_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../test_files/mirrulations_web_files/")
HOME = os.getenv("HOME")

AHRQ_path = "AHRQ_FRDOC/AHRQ_FRDOC_0001/AHRQ_FRDOC_0001-0036"


def make_replacement_zip(file):
    replacement = open(file, "w+")
    replacement.write("")
    replacement.close()


def test_add_readme():
    zipfile_path = add_PATH+"AHRQ_FRDOC_0001-0036.zip"
    dz.add_readme(zipfile_path, "AHRQ_FRDOC_0001-0036")
    archive = zipfile.ZipFile(zipfile_path)
    f = bytes.decode(archive.read('README.md'))
    assert f == "This is a README file for AHRQ_FRDOC_0001-0036"
    make_replacement_zip(zipfile_path)


def test_zip_directory():
    path = dz.zip_directory("AHRQ_FRDOC_0001-0036", PATH + AHRQ_path)
    archive = zipfile.ZipFile(path)
    f = bytes.decode(archive.read('README.md'))
    assert f == "This is a README file for AHRQ_FRDOC_0001-0036"
    os.remove(path)


#def test_Path():
#    path = zip_directory(PATH, 'test')
#    assert os.path.exists(path) == True
#    os.remove(path)


#def test_FileName():
#    path = zip_directory(PATH, 'test')
#    archive = zipfile.ZipFile(path)
#    assert archive.filename == 'zip_files/test.zip'
#    os.remove(path)


#def test_fileExists():
#    path = zip_directory(PATH, 'test')
#    archive = zipfile.ZipFile(path)
#    file_path = PATH + '/test.txt'
#    file_path = file_path[1:]
#    f = bytes.decode(archive.read(file_path))
#    assert f == 'This is a test file'
#    os.remove(path)

