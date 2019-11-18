import pytest
import prog_manage
from io import StringIO


# This is more of an init that removes and re-installs hamstall so we have a blank slate to work with for testing.


def test_reset(monkeypatch):
    with pytest.raises(SystemExit):
        prog_manage.erase()

    with pytest.raises(SystemExit):
        prog_manage.first_time_setup(True)

    with pytest.raises(SystemExit):
        monkeypatch.setattr('sys.stdin', StringIO("n\nn\nn\nn\nn\nn\nn\nn\nn\nn\nn\nn\nn\n"))
        prog_manage.install("./tests/fake_packages/package.tar.gz")
