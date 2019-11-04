import file
import prog_manage
import config
import json


def test_get_db():
    assert file.get_db() == {
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
            "package": {
                "desktops": []
            }
        }
    }


def test_name():
    assert file.name("/some/directory/file.tar.gz") == "file"
    assert file.name("~/i/was/home/but/now/im/here.zip") == "here"
    assert file.name("./tar/xz/files/are/pretty/cool.tar.xz") == "cool"


def test_extension():
    assert file.extension("weeeeee.zip") == ".zip"
    assert file.extension("asdf.tar.gz") == ".tar.gz"
    assert file.extension("afile.7z") == ".7z"
    assert file.extension("this_is_a_file.that.is.cool.tar.xz") == ".tar.xz"


def test_exists():
    assert file.exists("./file.py") is True
    assert file.exists("./file.no") is False


def test_spaceify():
    assert file.spaceify("this is a test") == "this\\ is\\ a\\ test"


def test_check_line():
    # TODO: Test other modes
    file.create("~/.hamstall/config")
    file.add_line("Test Line", "~/.hamstall/config")
    assert file.check_line("Test Line", "~/.hamstall/config", "fuzzy") is True
    assert file.check_line("ThisShouldNotBeFound=True", "~/.hamstall/config", "fuzzy") is False


def test_create():
    file.create("~/.hamstall/test01")
    assert file.exists("~/.hamstall/test01")


def test_remove_line():
    # TODO: Test other modes
    file.remove_line("Test Line", "~/.hamstall/config", "fuzzy")
    assert file.check_line("Verbose=False", "~/.hamstall/config", "fuzzy") is False


def test_add_line():
    file.add_line("Verbose=False\n", "~/.hamstall/config")
    assert file.check_line("Verbose=False", "~/.hamstall/config", "fuzzy") is True


def test_char_check():
    assert file.char_check("asdf") is False
    assert file.char_check("asdf ") is True
    assert file.char_check("as#df") is True


def test_write_db():
    old_db = file.db
    file.db.update({"test": "here"})
    file.write_db()
    old_db.update({"test": "here"})
    with open(file.full("~/.hamstall/database")) as f:
        db = json.load(f)
    assert old_db == db
