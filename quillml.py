class StringEntry:
    def __init__(self, value : str):
        if isinstance(value, str):
            self.value = value
        else:
            raise ValueError(f'Value must be of str type, got {type(value)} instead')

    def __repr__(self):
        return self.value


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


def _parse_entry_list(lines : list[tuple[int, str]], stopping_condition):
    entries = {}

    while True:
        line_number, line = lines[0]
        
        # test for ordinary variable
        first_equal_sign = line.find('=')
        if first_equal_sign != -1:
            variable_name = line[:first_equal_sign].strip()
            entry = parse_value(line[first_equal_sign+1:].strip())

            if variable_name not in entries:
                entries[variable_name] = entry
            else:
                raise QuillMLSyntaxError(f'Line {line_number}: repeat variable [{variable_name}]')
        elif line:
            raise QuillMLSyntaxError(f'Line {line_number}: [{line}] cannot be parsed')

        lines.pop(0)

        if len(lines) == 0:
            break

    return entries, lines

def _get_entry_list_string_repr(d : dict):
    string_list = []

    for k, v in d.items():
        string_list.append(f'{k} = {v}')

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

        self.entries = _parse_entry_list(lines, None)[0]

    def __getitem__(self, key):
        return self.entries[key]

    def __repr__(self):
        filepath_str = f'QuillML file [{self.filepath}]'
        return '\n'.join([filepath_str] + _get_entry_list_string_repr(self.entries))
