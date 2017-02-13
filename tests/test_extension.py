
def test_hello():
    import emzed.ext
    reload(emzed.ext)
    assert emzed.ext.target_identification.hello().startswith("hello")
    