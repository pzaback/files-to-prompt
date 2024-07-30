import os
from fnmatch import fnmatch
import click
from jinja2 import Environment, FileSystemLoader


def should_ignore(path, ignore_rules):
    """Checks if a file or directory should be ignored based on the provided rules."""
    for rule in ignore_rules:
        if fnmatch(os.path.basename(path), rule):
            return True
        if os.path.isdir(path) and fnmatch(os.path.basename(path) + "/", rule):
            return True
    return False


def read_ignore_file(path):
    """Reads an ignore file (.gitignore or custom) and returns a list of patterns."""
    if os.path.isfile(path):
        with open(path, "r") as f:
            return [
                line.strip() for line in f if line.strip() and not line.startswith("#")
            ]
    return []


def print_from_template(template_file, path, content, index):
    """Renders the content using the provided Jinja2 template."""
    env = Environment(loader=FileSystemLoader(os.path.dirname(template_file)))
    template = env.get_template(os.path.basename(template_file))
    rendered_content = template.render(content=content, path=path, index=index)
    click.echo(rendered_content)


def process_path(
    path,
    include_hidden,
    ignore_gitignore,
    ignore_files,  # List of ignore file paths
    ignore_patterns,
    template_file,
    index,
):
    ignore_rules = []
    if not ignore_gitignore:
        ignore_rules.extend(read_ignore_file(os.path.join(path, ".gitignore")))
    for ignore_file in ignore_files:
        ignore_rules.extend(read_ignore_file(ignore_file))

    if os.path.isfile(path):
        if should_ignore(path, ignore_rules):
            return index
        try:
            with open(path, "r") as f:
                content = f.read()
                if template_file:
                    print_from_template(template_file, path, content, index)
                else:
                    click.echo(path)
                    click.echo("---")
                    click.echo(content)
                    click.echo("---")
                index += 1
        except UnicodeDecodeError:
            warning_message = f"Warning: Skipping file {path} due to UnicodeDecodeError"
            click.echo(click.style(warning_message, fg="red"), err=True)

    elif os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            if not include_hidden:
                dirs[:] = [d for d in dirs if not d.startswith(".")]
                files = [f for f in files if not f.startswith(".")]

            dirs[:] = [
                d
                for d in dirs
                if not should_ignore(os.path.join(root, d), ignore_rules)
            ]
            files = [
                f
                for f in files
                if not should_ignore(os.path.join(root, f), ignore_rules)
            ]

            if ignore_patterns:
                files = [
                    f
                    for f in files
                    if not any(fnmatch(f, pattern) for pattern in ignore_patterns)
                ]
            for file in sorted(files):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r") as f:
                        content = f.read()
                        if template_file:
                            print_from_template(
                                template_file, file_path, content, index
                            )
                        else:
                            click.echo(file_path)
                            click.echo("---")
                            click.echo(content)
                            click.echo("---")
                        index += 1
                except UnicodeDecodeError:
                    warning_message = (
                        f"Warning: Skipping file {file_path} due to UnicodeDecodeError"
                    )
                    click.echo(click.style(warning_message, fg="red"), err=True)
    return index


@click.command()
@click.argument("paths", nargs=-1, type=click.Path(exists=True))
@click.option(
    "--include-hidden",
    is_flag=True,
    help="Include files and folders starting with .",
)
@click.option(
    "--ignore-gitignore",
    is_flag=True,
    help="Ignore .gitignore files and include all files",
)
@click.option(
    "ignore_patterns",
    "--ignore",
    multiple=True,
    default=[],
    help="List of patterns to ignore",
)
@click.option(
    "ignore_files",  # New option
    "--ignore-file",
    "-i",
    multiple=True,
    type=click.Path(exists=True),
    help="Path to an additional ignore file (can be used multiple times)",
)
@click.option(
    "--template-file",
    "-t",
    type=click.Path(exists=True),
    help="Path to a Jinja2 template file for formatting context items.",
)
@click.version_option()
def cli(
    paths,
    include_hidden,
    ignore_gitignore,
    ignore_patterns,
    ignore_files,
    template_file,
):
    """
    Takes one or more paths to files or directories and outputs every file,
    recursively, each one preceded with its filename like this:
    path/to/file.py
    ----
    Contents of file.py goes here
    ---
    path/to/file2.py
    ---
    ...
    """

    index = 1
    for path in paths:
        if not os.path.exists(path):
            raise click.BadArgumentUsage(f"Path does not exist: {path}")
        index = process_path(
            path,
            include_hidden,
            ignore_gitignore,
            ignore_files,  # Pass ignore_files to process_path
            ignore_patterns,
            template_file,
            index,
        )
