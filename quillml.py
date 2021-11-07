import re

class SingleEntry:
    """
    A single entry consists of a value and a dimension, e.g. "20 um".
    The dimension cannot exist for string values.
    """
    def __init__(self, value, dimension : str = None):
        if isinstance(value, list):
            valid_types = (int, float, str)
            array_type = None
            for t in valid_types:
                if all([isinstance(v, t) for v in value]):
                    array_type = t
            if array_type == str:
                if dimension is None:
                    self.value = value
                else:
                    raise ValueError(f'Arrays of string values cannot have a dimension, got [{dimension}]')
            elif array_type:
                self.value = value
            else:
                raise ValueError(f'Array [{value}] does not have permitted homogeneous types')
        elif isinstance(value, str):
            if dimension is None:
                self.value = value
            else:
                raise ValueError(f"String values cannot have a dimension, got [{dimension}]")
        elif isinstance(value, int) or isinstance(value, float):
            self.value = value
        else:
            raise ValueError(f'Got unexpected type {type(value)}')
        if dimension is None or isinstance(dimension, str):
            self.dimension = dimension
        else:
            raise ValueError(f'Dimension must be of str type, got {type(dimension)} instead')

    def __repr__(self):
        if isinstance(self.value, list):
            value_str = '[' + ', '.join([str(s) for s in self.value]) + ']'
        else:
            value_str = self.value
        if self.dimension is not None:
            return f'{value_str} {self.dimension}'
        else:
            return f'{value_str}'

    def __eq__(self, other):
        if isinstance(other, str):
            if self.value == other:
                return True
        elif isinstance(other, list):
            if self.dimension != other.dimension:
                return False
            if len(self.value) != len(other):
                return False
            for i in range(len(other)):
                if self.value[i] != other[i]:
                    return False
            return True
        elif self.value == other.value and self.dimension == other.dimension:
            return True
        else:
            return False

    def to_dict(self):
        if self.dimension is not None:
            return {'value': self.value, 'dimension' : self.dimension}
        else:
            return {'value': self.value}


class GroupEntry:
    """
    A group entry is an entry containing multiple other entries with unique names.
    """
    def __init__(self, value : dict):
        self.value = value

    def __getitem__(self, index):
        return self.value[index]

    def __setitem__(self, index, value):
        self.value[index] = value

    def __contains__(self, index):
        return index in self.value

    def items(self):
        return self.value.items()

    def to_dict(self):
        return {k: self.value[k].to_dict() for k in self.value}


def parse_value(string : str):
    string = string.strip()

    # array value
    if string.startswith('['):
        pos = string.find(']')
        array_strings = [s.strip() for s in string[1:pos].split(',')]
        array_type = None
        try:
            value = [int(s) for s in array_strings]
            array_type = int
        except:
            try:
                value = [float(s) for s in array_strings]
                array_type = float
            except:
                value = array_strings
                array_type = str
        
        dimension = string[pos+1:].strip()
        if not dimension:
            dimension = None
        
        if array_type == str:
            if dimension is None:
                return SingleEntry(value)
            else:
                raise ValueError(f"Array [{value}] is array of strings and is not allowed to have a dimension [{dimension}]")
        else:
            return SingleEntry(value, dimension)


    # scalar value
    else:
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
            return SingleEntry(value)
        else:
            raise ValueError(f"String [{string}] has str value [{value}] but also has dimension [{dimension}]")
    else:
        return SingleEntry(value, dimension)


class QuillMLSyntaxError(Exception):
    def __init__(self, message):
        super().__init__(message)


class _ParseType:
    FULL = 0
    GROUP = 1


def _parse_entry_list(lines : list[tuple[int, str]], parse_type : _ParseType):
    entries = GroupEntry({})

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
                p = subline.find(';')
                # additional entries on the same line
                if p != -1:
                    lines[0] = (line_number, subline[p+1:].strip())
                    value = subline[1:p].strip()
                else:
                    value = subline[1:].strip()
                    lines.pop(0)
                try:
                    entry = parse_value(value)
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
                lines[0] = (line_number, line[1:].strip())
                return entries, lines
            else:
                raise QuillMLSyntaxError(f'Line {line_number}: Unexpected closing "}}"')
        # something unexpected
        elif line:
            raise QuillMLSyntaxError(f'Line {line_number}: [{line}] cannot be parsed')
        else:
            lines.pop(0)

        if len(lines) == 0:
            if parse_type == _ParseType.FULL:
                return entries, lines
            elif parse_type == _ParseType.GROUP:
                raise QuillMLSyntaxError('Unexpected end of file before closing "}"')

    

def _get_entry_list_string_repr(d : GroupEntry, tab=0):
    string_list = []
    prefix = ' ' * tab

    for k, v in d.items():
        if isinstance(v, GroupEntry):
            string_list.append(f'{prefix}{k} {{')
            string_list += _get_entry_list_string_repr(v, tab+2)
            string_list.append(f'{prefix}}}')
        else:
            string_list.append(f'{prefix}{k} = {v}')

    return string_list

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
        return self.entries.to_dict()

    def to_json(self):
        import json
        return json.dumps(self.to_dict(), indent=2)
