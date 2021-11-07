import pytest
import quillml
import os
dirname = os.path.dirname(__file__)


def test_representation():
    test_dir = os.path.join(dirname, 'test_files')
    reference_dir = os.path.join(test_dir, 'json_reference')

    filenames = [f for f in os.listdir(test_dir) if f.endswith('.quillml')]

    for filename in filenames:
        path = os.path.join(test_dir, filename)
        path_ref = os.path.join(reference_dir, filename.replace('.quillml', '.json'))

        try:
            content = quillml.QuillMLFile(path)
            if os.path.exists(path_ref):
                with open(path_ref, 'r') as f:
                    lines_ref = f.read().split('\n')
                lines = content.to_json().split('\n')
                if (len(lines) != len(lines_ref)):
                    pytest.fail(f'Reference file length differs: {len(lines)} vs {len(lines_ref)} (reference)')
                for i in range(len(lines)):
                    if lines[i] != lines_ref[i]:
                        pytest.fail(f'Reference line {i} differs: [{lines[i]}] vs [{lines_ref[i]}]')
            else:
                with open(path_ref, "w") as f:
                    print(content.to_json(), end='', file=f)
        except quillml.QuillMLSyntaxError as error:
            if os.path.exists(path_ref):
                pytest.fail(f'JSON reference for {filename} exists, but the original cannot be parsed: {error}')