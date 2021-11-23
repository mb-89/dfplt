from dfplt import dfplt
from x2df import x2df


def test_Lineplot():
    assert dfplt.main(["test", "example_stepresponses1", "--nonblock"]) == 0


def test_Lineplot_fallback():
    dfs = x2df.load("example_stepresponses1")
    plots = [df.plot(_fallbackBackend=True) for df in dfs]
    dfplt.show(plots, block=False)
