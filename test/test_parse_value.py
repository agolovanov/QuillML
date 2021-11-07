import quillml


def test_strings():
    strings = ['True', 'False', 'electron', 'long_value']

    for s in strings:
        e = quillml.parse_value(s)
        assert isinstance(e.value, str)
        assert e.value == s


def test_simple_integers():
    strings = ['3', '-12345', '0']
    values = [int(s) for s in strings]

    for s, v in zip(strings, values):
        e = quillml.parse_value(s)

        assert isinstance(e.value, int)
        assert e.value == v
        assert e.dimension is None


def test_simple_floats():
    strings = ['0.0', '3.56e-32', '5.6', '-6.17', '-1.17e5']
    values = [float(s) for s in strings]

    for s, v in zip(strings, values):
        e = quillml.parse_value(s)

        assert isinstance(e.value, float)
        assert e.value == v
        assert e.dimension is None


def test_dimensional():
    int_strings = ['3', '-12345', '0']
    float_strings = ['0.0', '3.56e-32', '5.6', '-6.17', '-1.17e5']
    dimensions = ['GeV', 'cm', 'm/s^2']

    for d in dimensions:
        for i in int_strings:
            e = quillml.parse_value(f'{i} {d}')

            assert isinstance(e.value, int)
            assert e.value == int(i)
            assert e.dimension == d

        for f in float_strings:
            e = quillml.parse_value(f'{f} {d}')

            assert isinstance(e.value, float)
            assert e.value == float(f)
            assert e.dimension == d