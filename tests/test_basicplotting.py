from dfplt import examplegallery


def test_fallback(qtbot):
    eg = examplegallery.Examplegallery()
    qtbot.addWidget(eg)
    eg.be.setCurrentText("matplotlib")
    for example in eg.availableExamples:
        eg.ex.setCurrentText(example)
