#!/usr/bin/env python
import sys, os, os.path, tempfile, json, shutil, re, zipfile


"""
This program does the validation of data for the document jobs and then saves that data locally
"""


# General Functions
def get_document_id(file_name):
    """
    Extract the document id from the file name
    :param file_name: name of the file that the id will be extracted from
    :return id: the string of the document id from the file name
    """
    doc,id,ending = file_name.split(".")
    return id


def get_file_name(path):
    """
    Extracts the name of the file from the given path
    :param path: location of the file in which the name will be extracted from
    :return:
    """
    split_path = path.split("/")
    file_name = split_path[len(split_path) - 1]
    return file_name


def get_doc_attributes(file_name):
    """
    Get the organization(s), the docket_id and the document_id from a file name
    :param file_name: name of the file to extract attributes of the document name
    :return:
    """
    document_id = get_document_id(file_name)

    if "_" in document_id:
        split_name = re.split("[-_]", document_id)
        org = split_name[0] + "_" + split_name[1]
        docket_id = org + "_" + split_name[2]
        document_id = docket_id + "-" + split_name[3]
        return org, docket_id, document_id

    else:
        split_name = re.split("[-]", document_id)
        length = len(split_name)
        count = 0
        for x in range(length):
            if split_name[x].isdigit():
                break
            else:
                count += 1

        org_list = split_name[:count]
        org_list.sort()
        org = add_hyphens(org_list)
        docket_id = add_hyphens(split_name[:len(split_name) - 1])
        document_id = add_hyphens(split_name[:len(split_name)])

        return org,docket_id,document_id


def add_hyphens(list):
    """
    This returns the ordered list of the organizations in the docket. This will be useful for creating the directories
    :param list: the list to be hyphenated
    :return:
    """
    hyphened_string = ""
    for x in range(len(list)):

        if x == 0:
            if len(list) == 1:
                hyphened_string = list[x]
            else:
                hyphened_string = list[x] + "-"

        elif x == len(list) - 1:
            hyphened_string = hyphened_string + list[x]

        else:
            hyphened_string = hyphened_string + list[x] + "-"

    return hyphened_string


# Validator Functions
def ending_is_number(document):
    """
    Ensure that the document id ends in a number
    :param document: the document file containing the id
    :return:
    """
    list = re.split("-", document)
    number = list[-1]
    return number.isdigit()


def id_matches(path, doc_id):
    """
    Ensures that the ids of the documents match correctly
    :param path: the file that is being looked at
    :param doc_id: the document id to check
    :return:
    """
    f = open(path, "r")
    j = json.load(f)

    document_id = j["documentId"]["value"]

    return document_id == doc_id


def begining_is_letter(document):
    """
    Ensures that the beginning of the document id begins with a letter
    :param document: the document file containing the id
    :return:
    """
    letter = document[0]
    return letter.isalpha()


# Assimilation Functions
def local_save(cur_path, destination):
    """
    Save the file located at the current path to the destination location
    :param cur_path: location of the file to be saved
    :param destination: location that the file should be saved
    :return:
    """
    file_name = get_file_name(cur_path)
    org, docket_id, document_id = get_doc_attributes(file_name)
    destination_path = destination + org + "/" + docket_id + "/" + document_id + "/"
    create_new_dir(destination_path)
    shutil.copy(cur_path, destination_path + '/' + file_name)


def create_new_dir(path):
    """
    If the path does not exist, create the directory
    :param path: the path to the directory to be created
    :return:
    """
    if not os.path.exists(path):
        os.makedirs(path)


def get_file_list(compressed_file, PATHstr):
    """
    Get the list of files to be processed from a compressed file
    :param compressed_file: file containing file list to be uncompressed
    :param PATHstr: location of the file in string form
    :return:
    """
    files = zipfile.ZipFile(compressed_file, "r")
    files.extractall(PATHstr)

    # Create a list of all the files in the directory
    file_list = os.listdir(PATHstr)

    final_list = []
    for file in file_list:
        if file.startswith("doc"):
            final_list.append(file)

    return final_list


# Final Function
def process_doc(json_data, compressed_file, Redis_Manager):
    """
    Main doc function, called by the server to check and save documents returned from the client
    :param json_data: json data of the job
    :param compressed_file: compressed file of file names
    :param Redis_Manager: database manager
    :return:
    """

    if sff.job_exists_hash(json_data["job_id"], Redis_Manager, 'progress') is False:
        pass

    else:

        PATH = tempfile.mkdtemp()
        PATHstr = str(PATH)

        # Unzip the zipfile and then remove the tar file and create a list of all the files in the directory
        file_list = get_file_list(compressed_file, PATHstr)

        renew = False
        for file in file_list:
            org, docket_id, document_id = get_doc_attributes(file)

            if file.startswith("doc.") and begining_is_letter(document_id) and ending_is_number(document_id) and file.endswith(".json"):
                if id_matches(file, document_id):
                    pass
                else:
                    renew = False
                    break

            elif file.startswith("doc.") and ending_is_number(document_id) and begining_is_letter(document_id):
                    pass
            else:
                renew = True
                break

        if renew is True:
            sff.renew_job(json_data, Redis_Manager)

        else:
            for file in file_list:
                local_save(PATHstr + "/" + file, "~/regulations-data/")
            key = sff.get_key_hash(json_data["job_id"], Redis_Manager, "progress")
            sff.remove_job_hash(key, Redis_Manager, "progress")
