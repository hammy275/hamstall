import sys
import os
import pytest

import config

def test_read_config():
    assert config.read_config("Verbose") == False

def test_change_config():
    config.change_config("Verbose", "flip")
    assert config.read_config("Verbose") == True
    config.change_config("Verbose", "flip")
    assert config.read_config("Verbose") == False

def test_vcheck():
    assert config.vcheck() == False


