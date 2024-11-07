# EduML Cookiecutter Template

This is a [`copier`](https://copier.readthedocs.io) project template which sets
up a Git repository for creating machine learning jobs for the EduML cluster
hosted by the Faculty of Mathematics and Computer Science of the Babes-Bolyai
University in Romania.

## Prerequisites

Install a recent version of [Python](https://www.python.org). Using a tool like
[`pyenv`](https://github.com/pyenv/pyenv) is highly recommended. Once Python is
installed, make sure you have `copier` installed in the `PATH`.
You might use a tool such as [`pipx`](https://github.com/pypa/pipx) to do that.

```shell
$ pipx install copier
```

## Usage

Run Copier using the HTTP link to this repository.

```shell
$ copier copy https://github.com/koosie0507/cs-ubb-eduml-app.git path/to/local/dir
```

Once the project code is generated, follow the instructions in the `README.md`
file located in the project code directory to set up your ML training job on
EduML.