# QuillML

**QuillML** is a simple markup language specifically designed to make writing configuration files for particle-in-cell (PIC) codes easier.
It is a side project to the PIC code Quill (https://github.com/QUILL-PIC/Quill), but it can be used completely independently.

## Syntax and features

The syntax of QuillML is very flexible and can be adapted to configuration of various physical simulations.

The basic unit of the language is a simple key–value pair, where the value can be a number, a number + dimension, or a string:
```
particles_per_cell = 8
lambda = 1 um
nplasm = 1e18 1/cm^3
particle_pusher = boris
```
All entries must have unique names.

In addition to single numbers, the user can set arrays of ints, floats, or strings (with dimensions for numerical values):
```
box_size = [100, 60, 60]
x_coordinates = [0, 2.5, 4.5] cm
particles = [electron, positron, photon]
```

Several entitites can be grouped in a category
```
beam {
    species = electron
    particles_per_cell = [2, 2, 1]
    envelope { type = gaussian; center = [40, 20, 20] um; size = [10, 2, 2] um; }
    pusher = boris
}
```
Of course, creating nested subgroups of any depth is possible. Unique names are required only for variables in the same subgroup.

Also, as demonstrated above, the `;` operator can be used as a replacement for line separation to make some subgroups more compact.


## API

In order to use the API, you need a Python 3.6+ interpreter. There are no additional dependencies.

To load a configuration file into memory, use
```
import quillml
data = quillml.QuillMLFile('path/to/example.quillml')
```

The `QuillMLFile` object can be used like an ordinary Python dictionary.
Nested groups are available through a chain of keys, like `data['beam']['pusher'].value`.
It also supports sensible serialization to JSON via the `to_json` command to make integration with any other software (including PIC codes) easy.

## Testing

Run
```
python -m pytest .
```
in the root folder of the project.

Any valid `.quillml` file placed in the `test_files` folder will be automatically converted to reference QuillML and JSON in `reference` and `reference_json` subfolders, respectively.
