from dfplt import dfplt


def test_main():
    assert dfplt.main(["test", "-v"]) == 0
    assert dfplt.main(["test", "-?"]) == 0
    assert dfplt.main(["test", "examples_doesntExist"]) == 0
