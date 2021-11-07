import quillml
import random

def test_string_entry():
    strings = ['True', 'False', 'electron', 'long_value']

    for s in strings:
        e = quillml.SingleEntry(s)
        assert e.value == s


def test_number_entry():
    integers = [random.randint(-30000, 30000) for i in range(50)]
    floats = [0.0, 1e28, -.13] + [-50.0 + 100 * random.random() for i in range(50)]

    for i in integers:
        e = quillml.SingleEntry(i)

        assert e.dimension is None
        assert isinstance(e.value, int)
        assert e.value == i

    for f in floats:
        e = quillml.SingleEntry(f)

        assert e.dimension is None
        assert isinstance(e.value, float)
        assert e.value == f

    dimensions = ['cm', 'GeV/m', 'lambda']

    for d in dimensions:
        for i in integers:
            e = quillml.SingleEntry(i, d)

            assert e.dimension == d
            assert isinstance(e.value, int)
            assert e.value == i

        for f in floats:
            e = quillml.SingleEntry(f, d)

            assert e.dimension == d
            assert isinstance(e.value, float)
            assert e.value == f

    assert(str(quillml.SingleEntry(5)) == '5')
    assert(str(quillml.SingleEntry(5, 'GeV')) == '5 GeV')
    assert(str(quillml.SingleEntry(0.7, 'cm')) == '0.7 cm')
    assert(str(quillml.SingleEntry(-0.7)) == '-0.7')
    assert(str(quillml.SingleEntry(1e27)) == '1e+27')


def test_array_entry():
    lengths = [1, 5, 20, 1000]
    dimensions = ['cm', 'GeV/m', 'lambda']

    for d in dimensions:
        for l in lengths:
            integer_array = [random.randint(-30000, 30000) for i in range(l)]
            e = quillml.SingleEntry(integer_array, d)

            assert len(e.value) == l
            for i in range(l):
                assert e.value[i] == integer_array[i]
            assert e.dimension == d

            float_array = [-50 + 100 * random.random() for i in range(l)]
            e = quillml.SingleEntry(float_array, d)

            assert len(e.value) == l
            for i in range(l):
                assert e.value[i] == float_array[i]
            assert e.dimension == d
