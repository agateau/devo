# Format of devo-batchbuild yaml files

A devo-batchbuild yaml file is made of two main sections: "global" and "modules".

## Global section

Syntax:

    global:
      <option1>: <value>
      <option2>: <value>

Available options:

- base-dir: Where to checkout code.

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
  within `global/base-dir`.
- repo-type: Can be "git", "svn" or "kdegit".
- repo-url: Url of the repository.
- configure: Command to run to configure the source. Defaults to "devo-cmake".
- configure-options: Options to pass to the `configure` command.
- build: Command to run to build the source. Defaults to "make".
- build-options: Options to pass to the `build` command.
- auto: Whether this module should be build by default. Can be "true" or
  "false". Defaults to "true".

`name` is the only mandatory option.

Default for all of the module options can be overriden by specifying them in the
global section. Good candidates are `configure-options`, `build-options` or
`repo-type`.
