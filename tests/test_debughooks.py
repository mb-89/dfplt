from dfplt import dfplt
import sys
import pytest

trace = str(sys.gettrace())
debuggerAttached = not trace.startswith("<coverage.")
pytestmark = pytest.mark.skipif(
    not debuggerAttached,
    reason="These tests are debug-hooks and will be skipped during normal tests",
)


def test_examples():
    assert dfplt.main(["test", "--examples"]) == 0
