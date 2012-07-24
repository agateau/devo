# devo-batchbuild yaml files

## Global section

    global:
      base-dir: where to checkout code.

## Modules section

    modules:
    - name: name of module, will be used as dir name in `base-dir`.
      repo-type: can be "git", "svn" or "kdegit".
      repo-url: url of the repository.
      configure: command to run to configure the source. Defaults to "cmake".
      configure-options: options to pass to the `configure` command.
      build: command to run to build the source. Defaults to "make".
      build-options: options to pass to the `build` command.
      auto: whether this module should be build by default. Can be "true" or "false". Defaults to "true".

Default for most of the module options can be overriden by specifying them in
the global section. Good candidates are `configure-options`, `build-options` or
`repo-type`.
