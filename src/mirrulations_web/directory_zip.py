import shutil
import os
import re
import zipfile
import mirrulations.doc_filter as mc

home = os.getenv("HOME")


def zip_directory(document_id, directory_path):
    archive_name = document_id +'.zip'
    # root_dir parameter sets the directory to save without causing tarbombing
    # 4th parameter is what directory you are saving
    # TODO: Try adding a path along with the document id
    shutil.make_archive(document_id, "zip", root_dir=directory_path, base_dir=directory_path)
    add_readme(archive_name, document_id)
    return archive_name


def add_readme(zip_file, document_id):
    dir_zip = zipfile.ZipFile(zip_file, 'a')
    dir_zip.writestr('README.md', "This is a README file for " + document_id)
    dir_zip.close()


# def zip_directory(zip_path, filename):
#     "All its doing is adding the path to the filename User/ahaug/zipfiles/filename"
#     archive = os.path.expanduser(os.path.join('zip_files',filename))
#     shutil.make_archive(archive,'zip',root_dir='zip_files',base_dir=zip_path)
#     add_readme(archive+'.zip',filename)
#     return archive+'.zip'
#
#



