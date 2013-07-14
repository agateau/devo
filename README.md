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
