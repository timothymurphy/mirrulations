import os
import zipfile


def zip_directory_zip_version(zipfile_name, directory_path):
    if os.path.exists(directory_path):
        with zipfile.ZipFile(zipfile_name+'.zip', 'w', zipfile.ZIP_DEFLATED) as outZipFile:

            # The root directory within the ZIP file.
            rootdir = os.path.basename(directory_path)

            for dirpath, dirnames, filenames in os.walk(directory_path):
                for filename in filenames:
                    # Write the file named filename to the archive,
                    # giving it the archive name 'arcname'.
                    filepath = os.path.join(dirpath, filename)
                    parentpath = os.path.relpath(filepath, directory_path)
                    arcname = os.path.join(rootdir, parentpath)

                    outZipFile.write(filepath, arcname)

            outZipFile.writestr('README.md', 'This is a README file for ' + zipfile_name)

        return outZipFile

    else:
        return ''


def add_readme(zip_file, document_id):
    with zipfile.ZipFile(zip_file, 'a', zipfile.ZIP_DEFLATED) as outZipFile:
        outZipFile.writestr('README.md', 'This is a README file for ' + document_id)
