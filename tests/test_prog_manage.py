import pytest
import os
from io import StringIO

import prog_manage
import file, config

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
    assert file.check_line("export PATH=$PATH:~/.hamstall/bin/test_program # test_program", "~/.hamstall/.bashrc", "fuzzy")


def test_verbose_toggle():
    prog_manage.verbose_toggle()
    assert config.read_config("Verbose") == True
    prog_manage.verbose_toggle()
    assert config.read_config("Verbose") == False


def test_list_programs(capsys):
    with pytest.raises(SystemExit):
        prog_manage.list_programs()
    assert capsys.readouterr().out.rstrip("\n") == "package"


def test_uninstall():
    prog_manage.uninstall("package")
    assert file.check_line("export PATH=$PATH:~/.hamstall/bin/package # package", "~/.hamstall/.bashrc", "fuzzy") == False
    assert os.path.isfile(file.full("~/.hamstall/bin/package/test.sh")) == False


def test_erase():
    with pytest.raises(SystemExit):
        prog_manage.erase()
    assert os.path.isfile(file.full("~/.hamstall/hamstall.py")) == False
    assert file.check_line("source ~/.hamstall/.bashrc", "~/.bashrc", "fuzzy") == False
