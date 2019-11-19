import pytest
import prog_manage
import generic
from io import StringIO


# This is more of an init that removes and re-installs hamstall so we have a blank slate to work with for testing.


def test_reset(monkeypatch):
    assert prog_manage.erase() == "Erased" or prog_manage.erase() == "Not installed"

    prog_manage.first_time_setup(True)

    monkeypatch.setattr('sys.stdin', StringIO("n\nn\nn\nn\nn\nn\nn\nn\nn\nn\nn\nn\nn\n"))
    prog_manage.install("./tests/fake_packages/package.tar.gz")
