import fakeredis
import mock
import pytest
import requests_mock

from mirrulations_server.redis_manager import RedisManager

from mirrulations_server.doc_filter import *

PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../../tests/test_files/mirrulations_files/')


@pytest.fixture
def mock_req():
    with requests_mock.Mocker() as m:
        yield m


@pytest.fixture()
def work_temp_dir():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture()
def save_temp_dir():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@mock.patch('mirrulations_server.redis_manager.reset_lock')
@mock.patch('mirrulations_server.redis_manager.set_lock')
def make_database(reset, lock):
    r = RedisManager(fakeredis.FakeRedis())
    r.delete_all()
    return r


def make_temp_file(path):
    with open(path, 'w') as f:
        f.write('Stuff was written here')
    return f.name


def test_process_doc(save_temp_dir):
    redis_server = make_database()
    path_string = save_temp_dir

    json_data = json.dumps({'job_id': '1', 'type': 'doc',
                            'client_id': 'Alex', 'version': '0.0.0'})
    redis_server.add_to_progress(json_data)
    json_data = json.loads(json_data)

    compressed_file = PATH + 'test_result.zip'
    process_doc(redis_server, json_data, compressed_file, path_string)
    queue = redis_server.get_all_items_in_queue()
    progress = redis_server.get_all_items_in_progress()
    assert len(queue) == 0
    assert len(progress) == 0


def test_process_doc_bad_file(save_temp_dir):
    redis_server = make_database()
    path_string = save_temp_dir

    json_data = json.dumps({'job_id': '1', 'type': 'doc',
                            'client_id': 'Alex', 'version': '0.0.0'})
    redis_server.add_to_progress(json_data)
    json_data = json.loads(json_data)

    compressed_file = PATH + 'bad_result.zip'
    process_doc(redis_server, json_data, compressed_file, path_string)
    queue = redis_server.get_all_items_in_queue()
    progress = redis_server.get_all_items_in_progress()
    assert len(queue) == 1
    assert len(progress) == 0


def test_get_file_list(work_temp_dir, save_temp_dir):
    compressed_file = PATH + 'Archive.zip'
    path_str = save_temp_dir
    file_list = get_file_list(compressed_file, path_str + '/', '123')
    assert len(file_list[0]) == 4


def test_get_file_list_and_work(work_temp_dir, save_temp_dir):
    compressed_file = PATH + 'Archive.zip'
    path_str = save_temp_dir
    file_list = get_file_list(compressed_file, path_str + '/', '123')

    condition = True
    for file in file_list[0]:
        document_id = get_document_id(file)
        if file.startswith('doc.')\
                and document_id_ending_is_number(document_id)\
                and document_id_beginning_is_letter(document_id):
            pass
        else:
            condition = False
            break

    assert condition is True


def test_get_file_list_and_bad_work(save_temp_dir):
    compressed_file = PATH + 'Bad_Archive.zip'
    path_str = save_temp_dir
    file_list = get_file_list(compressed_file, path_str + '/', '123')

    condition = True
    for file in file_list[0]:
        document_id = get_document_id(file)
        if file.startswith('doc.')\
                and document_id_ending_is_number(document_id)\
                and document_id_beginning_is_letter(document_id):
            pass
        else:
            condition = False

    assert condition is False


def test_get_file_list_and_more_bad_work(save_temp_dir):
    compressed_file = PATH + 'Bad_Middle_Archive.zip'
    path_str = save_temp_dir
    file_list = get_file_list(compressed_file, path_str + '/', '123')

    condition = True
    for file in file_list[0]:
        document_id = get_document_id(file)
        if file.startswith('doc.')\
                and document_id_ending_is_number(document_id)\
                and document_id_beginning_is_letter(document_id):
            pass
        else:
            condition = False

    assert condition is False


def test_get_file_list_and_bad_number_work(save_temp_dir):
    compressed_file = PATH + 'Bad_Number_Archive.zip'
    path_str = save_temp_dir
    file_list = get_file_list(compressed_file, path_str + '/', '123')

    condition = True
    for file in file_list[0]:
        document_id = get_document_id(file)
        if file.startswith('doc.')\
                and document_id_ending_is_number(document_id)\
                and document_id_beginning_is_letter(document_id):
            pass
        else:
            condition = False

    assert condition is False


def test_check_if_document_needs_renew():
    assert check_if_document_needs_renew(
        'doc.FMCSA-1997-2350-21654.tif', {'type': 'doc'}, PATH) is False


def test_check_if_document_needs_renew_json():
    assert check_if_document_needs_renew(
        'doc.FMCSA-1997-2350-21654.json', {'type': 'doc'}, PATH) is False


def test_check_if_document_needs_renew_bad_json():
    assert check_if_document_needs_renew(
        'doc.FMCSA-1997-2350-21653.json', {'type': 'doc'}, PATH) is True


def test_get_document_id():
    assert get_document_id('doc.mesd-2018-234234-0001.json') == \
           'mesd-2018-234234-0001'


def test_get_document_id_special():
    assert get_document_id('doc.AHRQ_FRDOC_0001-0036.json') == \
           'AHRQ_FRDOC_0001-0036'


def test_get_document_id_other_special():
    assert get_document_id('doc.FDA-2018-N-0073-0002.json') == \
           'FDA-2018-N-0073-0002'


def test_is_document_beginning_good():
    assert document_id_beginning_is_letter('AHRQ_FRDOC_0001-0036') is True


def test_is_document_beginning_bad():
    assert document_id_beginning_is_letter('9147_FRDOC_0001-0036') is False


def test_id_matches_good():
    assert document_id_matches_json_id(
        PATH + 'doc.FMCSA-1997-2350-21654.json',
        'FMCSA-1997-2350-21654') is True


def test_is_document_ending_a_number():
    assert document_id_ending_is_number('FDA-2018-N-0073-0002') is True


def test_is_document_ending_a_number_special():
    assert document_id_ending_is_number('AHRQ_FRDOC_0001-0036') is True


def test_is_document_ending_a_word():
    assert document_id_ending_is_number('FDA-2018-N-0073-Abcd') is False


def test_is_document_ending_a_word_special():
    assert document_id_ending_is_number('AHRQ_FRDOC_0001-WXyz') is False


def test_id_matches_bad():
    assert document_id_matches_json_id(PATH + 'doc.FMCSA-1997-2350-21653.json',
                                          'FMCSA-1997-2350-21653') is False


def test_save_single_file_locally(work_temp_dir, save_temp_dir):
    filename = 'doc.FMCSA-1997-2350-21654.json'
    full_path = '/FMCSA/FMCSA-1997-2350/FMCSA-1997-2350-21654/doc.FMCSA-1997-2350-21654.json'

    path = work_temp_dir + '/' + filename
    with open(path, 'w') as f:
        f.write('Stuff was written here')

    save_single_file_locally(path, save_temp_dir + '/')
    final_path = save_temp_dir + full_path

    assert os.path.exists(final_path)


def test_save_files_locally(work_temp_dir, save_temp_dir):
    filename1 = 'doc.FMCSA-1997-2350-21654.json'
    filename2 = 'doc.FMCSA-1997-2350-21655.json'
    filename3 = 'doc.FMCSA-1997-2350-21656.json'

    full_path1 = \
        '/FMCSA/FMCSA-1997-2350/FMCSA-1997-2350-21654/' \
        'doc.FMCSA-1997-2350-21654.json'
    full_path2 = \
        '/FMCSA/FMCSA-1997-2350/FMCSA-1997-2350-21655/' \
        'doc.FMCSA-1997-2350-21655.json'
    full_path3 = \
        '/FMCSA/FMCSA-1997-2350/FMCSA-1997-2350-21656/' \
        'doc.FMCSA-1997-2350-21656.json'

    make_temp_file(work_temp_dir + '/' + filename1)
    make_temp_file(work_temp_dir + '/' + filename2)
    make_temp_file(work_temp_dir + '/' + filename3)

    final_path1 = save_temp_dir + full_path1
    final_path2 = save_temp_dir + full_path2
    final_path3 = save_temp_dir + full_path3

    file_list = [filename1, filename2, filename3]
    path = work_temp_dir + '/'
    save_all_files_locally(file_list, path, save_temp_dir + '/')

    assert os.path.exists(final_path1)
    assert os.path.exists(final_path2)
    assert os.path.exists(final_path3)


def test_get_file_name():
    assert get_file_name(PATH + 'doc.mesd-2018-234234-0001.json') == \
           'doc.mesd-2018-234234-0001.json'


def test_create_new_directory():
    test_path = PATH + 'check/'
    create_new_directory_for_path(test_path)
    assert os.path.exists(test_path)
    os.rmdir(test_path)
