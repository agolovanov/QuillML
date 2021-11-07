import re

class StringEntry:
    def __init__(self, value : str):
        if isinstance(value, str):
            self.value = value
        else:
            raise ValueError(f'Value must be of str type, got {type(value)} instead')

    def __repr__(self):
        return self.value

    def __eq__(self, other):
        if isinstance(other, str):
            if self.value == other:
                return True
        elif self.value == other.value:
            return True
        else:
            return False

    def to_dict(self):
        return {'value': self.value}


class NumberEntry:
    def __init__(self, value, dimension : str = None):
        if isinstance(value, int) or isinstance(value, float):
            self.value = value
        else:
            raise ValueError(f'Value must be of int or float type, got {type(value)} instead')
        if dimension is None or isinstance(dimension, str):
            self.dimension = dimension
        else:
            raise ValueError(f'Dimension must be of str type, got {type(dimension)} instead')

    def __repr__(self):
        if self.dimension is not None:
            return f'{self.value} {self.dimension}'
        else:
            return f'{self.value}'

    def __eq__(self, other):
        if self.value == other.value and self.dimension == other.dimension:
            return True
        else:
            return False

    def to_dict(self):
        if self.dimension is not None:
            return {'value': self.value, 'dimension' : self.dimension}
        else:
            return {'value': self.value}


def parse_value(string : str):
    string = string.strip()
    last_space = string.rfind(' ')
    if last_space != -1:
        dimension = string[last_space + 1:]
        value_str = string[:last_space].strip()
    else:
        dimension = None
        value_str = string
    try:
        value = int(value_str)
    except:
        try:
            value = float(value_str)
        except:
            value = value_str
    
    if isinstance(value, str):
        if dimension is None:
            return StringEntry(value)
        else:
            raise ValueError(f"String [{string}] has str value [{value}] but also has dimension [{dimension}]")
    else:
        return NumberEntry(value, dimension)


class QuillMLSyntaxError(Exception):
    def __init__(self, message):
        super().__init__(message)


class _ParseType:
    FULL = 0
    GROUP = 1


def _parse_entry_list(lines : list[tuple[int, str]], parse_type : _ParseType):
    entries = {}

    # variable name can contain letters, digits, hyphens, underscores; it must begin with a letter or underscore
    variable_name_regex_str = r'^([\w_][\w\d\-_]*)'
    variable_name_regex = re.compile(variable_name_regex_str)


    while True:
        line_number, line = lines[0]

        m = re.match(variable_name_regex, line)
        
        # this line is a variable
        if m:
            variable_name = m.group()

            subline = line[len(variable_name):].strip()

            # ordinary variable
            if subline.startswith('='):
                try:
                    entry = parse_value(subline[1:].strip())
                except ValueError as err:
                    raise QuillMLSyntaxError(f'Line {line_number}: error parsing entry [{variable_name}], message {err}')
            # group variable
            elif subline.startswith('{'):
                lines[0] = (line_number, subline[1:].strip())
                try:
                    entry, lines = _parse_entry_list(lines, _ParseType.GROUP)
                except QuillMLSyntaxError as err:
                    raise QuillMLSyntaxError(f'Line {line_number}: error parsing group [{variable_name}], message: {err}')
            else:
                raise QuillMLSyntaxError(f'Line {line_number}: unexpected symbol [{subline[0]}] \
                                           after variable [{variable_name}], only [=] and [{{] are possible')

            if variable_name not in entries:
                entries[variable_name] = entry
            else:
                raise QuillMLSyntaxError(f'Line {line_number}: repeat variable [{variable_name}]')
        # group closer
        elif line.startswith('}'):
            if parse_type == _ParseType.GROUP:
                lines[0] = (line_number, lines[0][1][1:].strip())
                return entries, lines
            else:
                raise QuillMLSyntaxError(f'Line {line_number}: Unexpected closing "}}"')
        # something unexpected
        elif line:
            raise QuillMLSyntaxError(f'Line {line_number}: [{line}] cannot be parsed')

        lines.pop(0)

        if len(lines) == 0:
            if parse_type == _ParseType.FULL:
                return entries, lines
            elif parse_type == _ParseType.GROUP:
                raise QuillMLSyntaxError('Unexpected end of file before closing "}"')

    

def _get_entry_list_string_repr(d : dict, tab=0):
    string_list = []
    prefix = ' ' * tab

    for k, v in d.items():
        if isinstance(v, dict):
            string_list.append(f'{prefix}{k} {{')
            string_list += _get_entry_list_string_repr(v, tab+2)
            string_list.append(f'{prefix}}}')
        else:
            string_list.append(f'{prefix}{k} = {v}')

    return string_list


def _to_dict_recursive(d : dict):
    d_new = {}

    for k, v in d.items():
        if isinstance(v, dict):
            d_new[k] = _to_dict_recursive(v)
        else:
            d_new[k] = v.to_dict()

    return d_new


class QuillMLFile:
    def __init__(self, filepath):
        self.filepath = filepath
        
        with open(filepath, "r") as f:
            lines = f.readlines()

        # remove whitespace and any comments
        for i in range(len(lines)):
            lines[i] = lines[i].strip().split('#')[0]

        lines = list(enumerate(lines, 1))

        self.entries = _parse_entry_list(lines, _ParseType.FULL)[0]

    def __getitem__(self, key):
        return self.entries[key]

    def __repr__(self):
        return '\n'.join(_get_entry_list_string_repr(self.entries))

    def to_dict(self):
        return _to_dict_recursive(self.entries)

    def to_json(self):
        import json
        return json.dumps(self.to_dict(), indent=2)
