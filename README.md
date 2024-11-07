# EduML Cookiecutter Template

This is a [`cookiecutter`](https://github.com/cookiecutter/cookiecutter)
template which helps someone set up a Git repository for creating machine
learning jobs for the EduML cluster hosted by the Faculty of Mathematics and
Computer Science of the Babes-Bolyai University in Romania.

## Prerequisites

Install a recent version of [Python](https://www.python.org). Using a tool like
[`pyenv`](https://github.com/pyenv/pyenv) is highly recommended. Once Python is
installed, make sure you have `cookiecutter` installed somewhere in your `PATH`.
You might use a tool such as [`pipx`](https://github.com/pypa/pipx) to do that.

```shell
$ pipx install cookiecutter
```

## Usage

Run Cookiecutter using the HTTP link to this repository.

```shell
$ cd dir/where/you/want/to/create/your/ml/training/job
$ cookiecutter https://github.com/koosie0507/cs-ubb-eduml-app.git
```

If you want to generate the ML training job project in another folder than the
current working directory, use the `-o` flag. Cookiecutter has many other
useful command line options.

Once the project is generated, follow the instructions in its `README.md` file.