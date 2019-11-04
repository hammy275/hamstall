import config
import os


def test_read_config():
    assert config.read_config("Verbose") is False


def test_change_config():
    config.change_config("Verbose", "flip")
    assert config.read_config("Verbose") is True
    config.change_config("Verbose", "flip")
    assert config.read_config("Verbose") is False


def test_vcheck():
    assert config.vcheck() is False


def test_lock():
    config.lock()
    assert os.path.isfile("/tmp/hamstall-lock")


def test_locked():
    assert config.locked() == os.path.isfile("/tmp/hamstall-lock")


def test_unlock():
    config.unlock()
    assert not os.path.isfile("/tmp/hamstall-lock")