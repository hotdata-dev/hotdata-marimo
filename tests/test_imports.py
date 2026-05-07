def test_package_imports():
    import hotdata_marimo as hm

    assert hm.HotdataClient is not None
    assert hm.SqlEditor is not None
