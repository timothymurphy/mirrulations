import pytest
import os

import tempfile
from mirrulations.APIKeySetup import writeAPIKey

def test_no_dir():
    temp_dir = tempfile.TemporaryDirectory()

    writeAPIKey("secret_key", temp_dir.name + "/.env")

    file = open(temp_dir.name + "/.env/regulationskey.txt", "r")

    assert file.readline() == "secret_key\n"
    assert len(file.readline()) == 16

    file.close()
    temp_dir.cleanup()


def test_no_file():
    temp_dir = tempfile.TemporaryDirectory()

    writeAPIKey("secret_key", temp_dir.name)

    file = open(temp_dir.name + "/regulationskey.txt", "r")

    assert file.readline() == "secret_key\n"
    assert len(file.readline()) == 16

    file.close()
    temp_dir.cleanup()

def test_no_overwrite():
    temp_dir = tempfile.TemporaryDirectory()

    writeAPIKey("secret_key", temp_dir.name)
    writeAPIKey("spooky_key", temp_dir.name)

    file = open(temp_dir.name + "/regulationskey.txt", "r")

    assert file.readline() == "secret_key\n"
    assert len(file.readline()) == 16

    file.close()
    temp_dir.cleanup()