import quillml

def test_string_entry():
    strings = ['True', 'False', 'electron', 'long_value']

    for s in strings:
        e = quillml.StringEntry(s)
        assert e.value == s


def test_number_entry():
    integers = [-30, 0, 1200]
    floats = [0.0, 1e28, -.13]

    for i in integers:
        e = quillml.NumberEntry(i)

        assert e.dimension is None
        assert isinstance(e.value, int)
        assert e.value == i

    for f in floats:
        e = quillml.NumberEntry(f)

        assert e.dimension is None
        assert isinstance(e.value, float)
        assert e.value == f

    dimensions = ['cm', 'GeV/m', 'lambda']

    for d in dimensions:
        for i in integers:
            e = quillml.NumberEntry(i, d)

            assert e.dimension == d
            assert isinstance(e.value, int)
            assert e.value == i

        for f in floats:
            e = quillml.NumberEntry(f, d)

            assert e.dimension == d
            assert isinstance(e.value, float)
            assert e.value == f

    assert(str(quillml.NumberEntry(5)) == '5')
    assert(str(quillml.NumberEntry(5, 'GeV')) == '5 GeV')
    assert(str(quillml.NumberEntry(0.7, 'cm')) == '0.7 cm')
    assert(str(quillml.NumberEntry(-0.7)) == '-0.7')
    assert(str(quillml.NumberEntry(1e27)) == '1e+27')