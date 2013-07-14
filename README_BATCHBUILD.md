# Format of devo-batchbuild yaml files

A devo-batchbuild yaml file is made of two main sections: "global" and "modules".

## Global section

Syntax:

    global:
      <option1>: <value>
      <option2>: <value>

Available options:

- configure-options
- build-options
- repo-type

## Modules section

Syntax:

    modules:
    - <module1-option1>: <value>
      <module1-option2>: <value>
      <module1-option3>: <value>
    - <module2-option1>: <value>
      <module2-option2>: <value>

Available options:

- name: Name of module, code for the module will be kept in a dir with this name
  within `$DEVO_SOURCE_BASE_DIR`.
- repo-type: Can be "git", "svn" or "kdegit".
- repo-url: Url of the repository.
- branch: Branch to checkout (git only).
- configure: Command to run to configure the source. Defaults to "devo-cmake".
- configure-options: Options to pass to the `configure` command.
- build: Command to run to build the source. Defaults to "make".
- build-options: Options to pass to the `build` command.
- auto: Whether this module should be build by default. Can be "true" or
  "false". Defaults to "true".

`name` is the only mandatory option.

Default for all of the module options can be overridden by specifying them in the
global section. Good candidates are `configure-options`, `build-options` or
`repo-type`.

Commands listed in `configure`, `build` and `install` can use the
`DEVO_SOURCE_DIR` and `DEVO_BUILD_DIR` environment variables. When the command
is running those variables respectively contain the name of the source dir and
build dir for the component. That is, for a component named `foo`, variables
are set like this:

    DEVO_SOURCE_DIR=$DEVO_SOURCE_BASE_DIR/foo
    DEVO_BUILD_DIR=$DEVO_BUILD_BASE_DIR/foo

# `_base.yaml`

You may want to define a `_base.yaml` file to define default values for all
.yaml files.  This is quite handy for example to define the `build-options`
option.
