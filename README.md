# devo - Developer Overlay

Devo is a system to define custom environments to build and install software
using different settings.

The idea is to define separate build and install dirs, in your home dir.

Here is an example of what the dir hierarchy could look like:

    $HOME/
        src
            libfoo
            fooserver
            bar
        build
            overlay1
                libfoo
                fooserver
            overlay2
                bar
        install
            overlay1
                bin
                share
                lib
                ...
            overlay2
                bin
                share
                lib
                ...

With such a setup, one could start a shell on using `overlay1` like this:

    devo_sh overlay1

After this command, assuming `overlay1` has been correctly set up,
`$HOME/install/overlay1/bin` would be in $PATH, making it possible to run
software installed there.

If libfoo uses the CMake build system, one can then build it with:

    cd $HOME/build/overlay1/libfoo
    devo_cmake
    make
    make install

Devo also provides handy commands to switch dirs, `devo_cb` changes to the build
dir, `devo_cs` changes to the source dir.

    cd $HOME/src/libfoo

    devo_cb
    # $PWD is now $HOME/build/overlay1/libfoo

    devo_cs
    # $PWD is now $HOME/src/libfoo

`devo_cmake` is also smart enough to run in the build dir, and Devo comes with a
thin wrapper for `make`: `devo_make` which brings build dir awareness as well,
so one can also build libfoo like this:

    cd $HOME/src/libfoo
    devo_cmake
    devo_make
    devo_make install

## Variables used by Devo

- `$DEVO_NAME`: The name of the overlay ("overlay1" or "overlay2")

- `$DEVO_SOURCE_BASE_DIR`: Where source is stored ($HOME/src). Can be common, or
specific to an overlay.

- `$DEVO_BUILD_BASE_DIR`: Where build dirs for component will be created
($HOME/build/overlay1)

- `$DEVO_BUILD_BASE_ROOT_DIR`: The dir which contains all `$DEVO_BUILD_BASE_DIR`
($HOME/build)

- `$DEVO_PREFIX`: The dir where components will be installed
  ($HOME/install/overlay1)

## Initial setup

First, add the following lines to your shell:

    export DEVO_BUILD_BASE_ROOT_DIR=/path/to/build/root/dir
    . /path/to/devo/lib/devo/devo-setup.source

Then, create `~/.devo/`. This dir will contain all the overlay definitions.

## Creating an overlay

Create an overlay file in `~/.devo/`. The file name is used as the overlay name.
This file is a shell script which should at least define the following
variables:

- `$DEVO_PREFIX`
- `$DEVO_SOURCE_BASE_DIR`

It may also define:

- `$DEVO_CMAKE_BUILD_TYPE`: Build type argument passed by `devo_cmake` to `cmake`.

And other variables relevant for your environment:

- `$PATH`
- `$PKG_CONFIG_PATH`
- ...

TODO: document `_devo_prepend_prefix`.

## Tools

### `devo_sh`

Starts a new shell with the specified overlay loaded:

    devo_sh work

Starts a new shell with the "work" overlay. Leave the shell with Ctrl+D or
`exit` to unload all the changes.

### `devo_setup`

Loads an overlay in the current shell:

    devo_setup work

Loads the "work" overlay.

### `devo_cmake`

Run `cmake` with the right prefix and build type option. Usage:

    devo_cmake /path/to/source/dir

When run without an argument, it tries to figure out the source dir using
`$DEVO_SOURCE_BASE_DIR` and the base name of the current dir.

For example if you run `devo_cmake` from dir `$DEVO_BUILD_BASE_DIR/foo`, it
will use `$DEVO_SOURCE_BASE_DIR/foo` as the source dir.

### `devo_make`

Wrapper around make: switch to the build dir and runs make from there.

### `devo_run`

Run a command using a specific overlay:

    devo_run work mytool arg1 arg2

Loads the "work" overlay and runs `mytool arg1 arg2`.

### `devo_cb`

When in a source dir, change to the matching build dir.

If a matching build dir does not exist, try to find an existing parent build
dir, for example given this setup:

    $DEVO_SOURCE_BASE_DIR
        prj1
            foo

    $DEVO_BUILD_BASE_DIR
        prj1

If you are in `$DEVO_SOURCE_BASE_DIR/prj1/foo`, `devo_cb` will switch to
`$DEVO_BUILD_BASE_DIR/prj1`.

If no build dir can be found but user is in a source dir, `devo_cb` offers to
create it.

When outside of a source dir, `devo_cb` prints an error.

### `devo_cs`

When in a build dir, change to the matching source dir if it exists, otherwise
stays there.

## The `~/.devo/_base` file

You can create a `~/.devo/_base` file defining common environment variables.
This file is sourced before loading a new overlay.

Here is an example:

    export PATH=$HOME/bin:/usr/local/bin:/usr/bin:/bin
    export CC=$HOME/opt/cc/gcc
    export CXX=$HOME/opt/cc/g++

## Shell integration goodies

When an overlay is loaded, the `$DEVO_NAME` variable contains its name. It can
be handy to add this to your prompt.

Zsh users can add the following to their `.zshrc`:

    cd() {
        builtin cd $*
        devo_setup_from_pwd
    }

This makes Devo load the matching overlay when cd-ing to an overlay build dir.

TODO: Find the bash equivalent
