import pytest
import os
from io import StringIO

import prog_manage
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


def nothing_two(a, b=False):
    return None


def test_gitinstall(monkeypatch):
    monkeypatch.setattr(prog_manage, "finish_install", nothing_two)
    prog_manage.gitinstall("https://github.com/hammy3502/hamstall.git", "hamstall")
    assert os.path.isfile(os.path.expanduser("~/.hamstall/bin/hamstall/prog_manage.py"))


def test_get_file_version():
    assert prog_manage.get_file_version("prog") == config.prog_internal_version
    assert prog_manage.get_file_version("file") == config.file_version


def test_pathify():
    prog_manage.pathify("package")
    assert config.check_line("export PATH=$PATH:~/.hamstall/bin/package # package", "~/.hamstall/.bashrc", "fuzzy")
    prog_manage.pathify("test_program")
    assert config.check_line("export PATH=$PATH:~/.hamstall/bin/test_program # test_program", "~/.hamstall/.bashrc",
                           "fuzzy")


def test_verbose_toggle():
    prog_manage.verbose_toggle()
    assert config.read_config("Verbose") is True
    prog_manage.verbose_toggle()
    assert config.read_config("Verbose") is False


def test_list_programs(capsys):
    prog_manage.list_programs() == ["package"]


def test_create_desktop(monkeypatch):
    prog_manage.create_desktop("package", "Name", "test.sh", "Comment here", "False")
    assert config.exists("~/.local/share/applications/test.sh-package.desktop")


def test_remove_desktop():
    prog_manage.remove_desktop("package", "test.sh-package")
    assert not config.exists("~/.local/share/applications/test.sh-package.desktop")


def test_uninstall():
    prog_manage.uninstall("package")
    assert config.check_line("export PATH=$PATH:~/.hamstall/bin/package # package", "~/.hamstall/.bashrc",
                           "fuzzy") is False
    assert os.path.isfile(config.full("~/.hamstall/bin/package/test.sh")) is False


def test_install(monkeypatch):
    os.chdir(os.path.realpath(__file__)[:-19])
    monkeypatch.setattr(prog_manage, "finish_install", nothing_two)
    prog_manage.install("./fake_packages/package.tar.gz")
    assert os.path.isfile(os.path.expanduser("~/.hamstall/bin/package/test.sh"))


def test_create_db():
    prog_manage.create_db()
    #TODO: Fake os so we can test get_shell_file in any environment
    assert config.db == {
        "options": {
            "Verbose": False,
            "AutoInstall": False,
            "ShellFile": config.get_shell_file()
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
    assert prog_manage.erase() == "Erased"
    assert os.path.isfile(config.full("~/.hamstall/hamstall.py")) is False
    assert config.check_line("source ~/.hamstall/.bashrc", "~/.bashrc", "fuzzy") is False
