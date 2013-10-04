# devo - Developer Overlay

Devo is a system to define custom environments to build and install software
using different settings.

## Initial setup

- Make sure your shell sources `devo-setup.source`
- Add devo dir to $PATH or symlink all `devo-*` binaries to a dir in $PATH.

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

    export PATH=$HOME/bin:/usr/local/bin:/usr/bin:/bin
    export CC=$HOME/opt/cc/gcc
    export CXX=$HOME/opt/cc/g++

## Tools

### `devo_setup`

Loads an overlay in the current shell:

    devo_setup work

Loads the "work" overlay.

### `devo-cmake`

Run `cmake` with the right prefix and build type option. Usage:

    devo-cmake /path/to/source/dir

When run without an argument, it tries to figure out the source dir using
`$DEVO_SOURCE_BASE_DIR` and the base name of the current dir.

For example if you run `devo-cmake` from dir `$DEVO_BUILD_BASE_DIR/foo`, it
will use `$DEVO_SOURCE_BASE_DIR/foo` as the source dir.

### `devo-make`

Wrapper around make: switch to the build dir and runs make from there.

### `devo-run`

Run a command using a specific overlay:

    devo-run work mytool arg1 arg2

Loads the "work" overlay and runs `mytool arg1 arg2`.

### `devo_cb`

When in a source dir, change to the matching build dir.

If a matching build dir does not exist, try to find an existing parent build
dir, for example given this setup:

    + $DEVO_SOURCE_BASE_DIR
    '-+ prj1
      '- foo

    + $DEVO_BUILD_BASE_DIR
    '- prj1

If you are in `$DEVO_SOURCE_BASE_DIR/prj1/foo`, `devo-cb` will switch to
`$DEVO_BUILD_BASE_DIR/prj1`.

If no build dir can be found but user is in a source dir, `devo-cb` offers to
create it.

When outside of a source dir, prints an error.

### `devo_cs`

When in a build dir, change to the matching source dir if it exists, otherwise
stays there.
