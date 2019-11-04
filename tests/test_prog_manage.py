import pytest
import os
from io import StringIO

import prog_manage
import file
import config

"""
To write tests for:
update

manage
binlink
dirinstall
get_online_version
get_file_version
download_files
"""


def test_pathify():
    prog_manage.pathify("package")
    assert file.check_line("export PATH=$PATH:~/.hamstall/bin/package # package", "~/.hamstall/.bashrc", "fuzzy")
    prog_manage.pathify("test_program")
    assert file.check_line("export PATH=$PATH:~/.hamstall/bin/test_program # test_program", "~/.hamstall/.bashrc",
                           "fuzzy")


def test_verbose_toggle():
    prog_manage.verbose_toggle()
    assert config.read_config("Verbose") is True
    prog_manage.verbose_toggle()
    assert config.read_config("Verbose") is False


def test_list_programs(capsys):
    with pytest.raises(SystemExit):
        prog_manage.list_programs()
    assert capsys.readouterr().out.rstrip("\n") == "package"


def test_create_desktop(monkeypatch):
    monkeypatch.setattr("sys.stdin", StringIO("test.sh\nComment here\nn\nName Here\n\nend\n"))
    prog_manage.create_desktop("package")
    assert file.exists("~/.local/share/applications/test.sh-package.desktop")


def test_remove_desktop(monkeypatch):
    monkeypatch.setattr("sys.stdin", StringIO("test.sh-package"))
    prog_manage.remove_desktop("package")
    assert not file.exists("~/.local/share/applications/test.sh-package.desktop")


def test_uninstall():
    prog_manage.uninstall("package")
    assert file.check_line("export PATH=$PATH:~/.hamstall/bin/package # package", "~/.hamstall/.bashrc",
                           "fuzzy") is False
    assert os.path.isfile(file.full("~/.hamstall/bin/package/test.sh")) is False


def test_create_db():
    prog_manage.create_db()
    #TODO: Fake os so we can test get_shell_file in any environment
    assert file.db == {
        "options": {
            "Verbose": False,
            "AutoInstall": False,
            "ShellFile": prog_manage.get_shell_file()
        },
        "version": {
            "file_version": config.file_version,
            "prog_internal_version": config.prog_internal_version,
            "branch": "master"
        },
        "programs": {
        }
    }


def test_erase():
    with pytest.raises(SystemExit):
        prog_manage.erase()
    assert os.path.isfile(file.full("~/.hamstall/hamstall.py")) is False
    assert file.check_line("source ~/.hamstall/.bashrc", "~/.bashrc", "fuzzy") is False
