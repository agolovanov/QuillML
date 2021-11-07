import pytest
import quillml
import os
dirname = os.path.dirname(__file__)


def test_basic():
    filepaths = ['test_files/01-basic.quillml', 'test_files/01-basic-comment-whitespace.quillml']

    for filepath in filepaths:
        f = quillml.QuillMLFile(os.path.join(dirname, filepath))

        assert isinstance(f['x'].value, int)
        assert f['x'].value == 10
        assert f['x'].dimension is None

        assert isinstance(f['y'].value, float)
        assert f['y'].value == 100.0
        assert f['y'].dimension is None

        assert isinstance(f['long_variable'].value, float)
        assert f['long_variable'].value == 1e-24
        assert f['long_variable'].dimension == 'um'

        assert isinstance(f['myname'].value, int)
        assert f['myname'].value == -3
        assert f['myname'].dimension == 'cm'


def test_basic_repeat():
    with pytest.raises(quillml.QuillMLSyntaxError) as excinfo:
        f = quillml.QuillMLFile(os.path.join(dirname, 'test_files/02-basic-repeat.quillml'))
    assert "repeat variable [x]" in str(excinfo.value)

def test_group():
    f = quillml.QuillMLFile(os.path.join(dirname, 'test_files/03-group-basic.quillml'))

    assert f['group_name']['x'] == quillml.parse_value('10 um')
    assert f['group_name']['y'] == quillml.parse_value('50 mm')
    assert f['group_name']['long_variable'] == quillml.parse_value('1e12')
    assert f['group_name']['bool_variable'] == 'False'