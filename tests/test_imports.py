def test_package_imports():
    import hotdata_marimo as hm

    assert hm.HotdataClient is not None
    assert hm.SqlEditor is not None
    assert hm.register_hotdata_sql_engine is not None
    assert hm.HotdataMarimoEngine is not None
