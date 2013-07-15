# devo - Developer Overlay

Devo is a system to define custom environments to build and install software
using different settings.

## Creating an overlay

Create `~/.config/devo/`

Create an overlay file in it. This file should at least define the following
variables:

- `DEVO_PREFIX`: Directory where components should be installed
- `DEVO_BUILD_BASE_DIR`: Directory containing build dirs for components

It may also define the following variables:

- `DEVO_CMAKE_BUILD_TYPE`: Build type argument passed to CMake
- `DEVO_SOURCE_BASE_DIR`: Directory containing source dirs for components

## `_base` file

You can create a `~/.config/devo/_base` file defining common environment
variables definitions. Here is an example:

    export PATH=/home/aurelien/bin:/home/aurelien/etc/bin:/usr/local/bin:/usr/bin:/bin
    export CC=/home/aurelien/opt/cc/gcc
    export CXX=/home/aurelien/opt/cc/g++

## Tools

### `devo_setup.sh`

Loads an overlay in the current shell:

    devo_setup.sh work

Loads the "work" overlay.

### `devo-cmake`

Run `cmake` with the right prefix and build type option. Usage:

    devo-cmake /path/to/source/dir

When run without an argument, it tries to figure out the source dir using
`$DEVO_SOURCE_BASE_DIR` and the base name of the current dir.

For example if you run `devo-cmake` from dir `$DEVO_BUILD_BASE_DIR/foo`, it
will use `$DEVO_SOURCE_BASE_DIR/foo` as the source dir.

### `devo-run`

Run a command using a specific overlay:

    devo-run work mytool arg1 arg2

Loads the "work" overlay and runs `mytool arg1 arg2`.
