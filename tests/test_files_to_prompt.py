import os
from click.testing import CliRunner
from files_to_prompt.cli import cli


def test_basic_functionality(tmpdir):
    runner = CliRunner()
    with tmpdir.as_cwd():
        os.makedirs("test_dir")
        with open("test_dir/file1.txt", "w") as f:
            f.write("Contents of file1")
        with open("test_dir/file2.txt", "w") as f:
            f.write("Contents of file2")
        result = runner.invoke(cli, ["test_dir"])
        assert result.exit_code == 0
        assert "test_dir/file1.txt" in result.output
        assert "Contents of file1" in result.output
        assert "test_dir/file2.txt" in result.output
        assert "Contents of file2" in result.output


def test_include_hidden(tmpdir):
    runner = CliRunner()
    with tmpdir.as_cwd():
        os.makedirs("test_dir")
        with open("test_dir/.hidden.txt", "w") as f:
            f.write("Contents of hidden file")
        result = runner.invoke(cli, ["test_dir"])
        assert result.exit_code == 0
        assert "test_dir/.hidden.txt" not in result.output
        result = runner.invoke(cli, ["test_dir", "--include-hidden"])
        assert result.exit_code == 0
        assert "test_dir/.hidden.txt" in result.output
        assert "Contents of hidden file" in result.output


def test_ignore_gitignore(tmpdir):
    runner = CliRunner()
    with tmpdir.as_cwd():
        os.makedirs("test_dir")
        with open("test_dir/.gitignore", "w") as f:
            f.write("ignored.txt")
        with open("test_dir/ignored.txt", "w") as f:
            f.write("This file should be ignored")
        with open("test_dir/included.txt", "w") as f:
            f.write("This file should be included")
        result = runner.invoke(cli, ["test_dir"])
        assert result.exit_code == 0
        assert "test_dir/ignored.txt" not in result.output
        assert "test_dir/included.txt" in result.output
        result = runner.invoke(cli, ["test_dir", "--ignore-gitignore"])
        assert result.exit_code == 0
        assert "test_dir/ignored.txt" in result.output
        assert "This file should be ignored" in result.output
        assert "test_dir/included.txt" in result.output


def test_multiple_paths(tmpdir):
    runner = CliRunner()
    with tmpdir.as_cwd():
        os.makedirs("test_dir1")
        with open("test_dir1/file1.txt", "w") as f:
            f.write("Contents of file1")
        os.makedirs("test_dir2")
        with open("test_dir2/file2.txt", "w") as f:
            f.write("Contents of file2")
        with open("single_file.txt", "w") as f:
            f.write("Contents of single file")
        result = runner.invoke(cli, ["test_dir1", "test_dir2", "single_file.txt"])
        assert result.exit_code == 0
        assert "test_dir1/file1.txt" in result.output
        assert "Contents of file1" in result.output
        assert "test_dir2/file2.txt" in result.output
        assert "Contents of file2" in result.output
        assert "single_file.txt" in result.output
        assert "Contents of single file" in result.output


def test_ignore_patterns(tmpdir):
    runner = CliRunner()
    with tmpdir.as_cwd():
        os.makedirs("test_dir")
        with open("test_dir/file_to_ignore.txt", "w") as f:
            f.write("This file should be ignored due to ignore patterns")
        with open("test_dir/file_to_include.txt", "w") as f:
            f.write("This file should be included")
        result = runner.invoke(cli, ["test_dir", "--ignore", "*.txt"])
        assert result.exit_code == 0
        assert "test_dir/file_to_ignore.txt" not in result.output
        assert "This file should be ignored due to ignore patterns" not in result.output
        assert "test_dir/file_to_include.txt" not in result.output
        result = runner.invoke(cli, ["test_dir", "--ignore", "file_to_ignore.*"])
        assert result.exit_code == 0
        assert "test_dir/file_to_ignore.txt" not in result.output
        assert "This file should be ignored due to ignore patterns" not in result.output
        assert "test_dir/file_to_include.txt" in result.output
        assert "This file should be included" in result.output


def test_mixed_paths_with_options(tmpdir):
    runner = CliRunner()
    with tmpdir.as_cwd():
        os.makedirs("test_dir")
        with open("test_dir/.gitignore", "w") as f:
            f.write("ignored_in_gitignore.txt\n.hidden_ignored_in_gitignore.txt")
        with open("test_dir/ignored_in_gitignore.txt", "w") as f:
            f.write("This file should be ignored by .gitignore")
        with open("test_dir/.hidden_ignored_in_gitignore.txt", "w") as f:
            f.write("This hidden file should be ignored by .gitignore")
        with open("test_dir/included.txt", "w") as f:
            f.write("This file should be included")
        with open("test_dir/.hidden_included.txt", "w") as f:
            f.write("This hidden file should be included")
        with open("single_file.txt", "w") as f:
            f.write("Contents of single file")
        result = runner.invoke(cli, ["test_dir", "single_file.txt"])
        assert result.exit_code == 0
        assert "test_dir/ignored_in_gitignore.txt" not in result.output
        assert "test_dir/.hidden_ignored_in_gitignore.txt" not in result.output
        assert "test_dir/included.txt" in result.output
        assert "test_dir/.hidden_included.txt" not in result.output
        assert "single_file.txt" in result.output
        assert "Contents of single file" in result.output
        result = runner.invoke(cli, ["test_dir", "single_file.txt", "--include-hidden"])
        assert result.exit_code == 0
        assert "test_dir/ignored_in_gitignore.txt" not in result.output
        assert "test_dir/.hidden_ignored_in_gitignore.txt" not in result.output
        assert "test_dir/included.txt" in result.output
        assert "test_dir/.hidden_included.txt" in result.output
        assert "single_file.txt" in result.output
        assert "Contents of single file" in result.output
        result = runner.invoke(
            cli, ["test_dir", "single_file.txt", "--ignore-gitignore"]
        )
        assert result.exit_code == 0
        assert "test_dir/ignored_in_gitignore.txt" in result.output
        assert "test_dir/.hidden_ignored_in_gitignore.txt" not in result.output
        assert "test_dir/included.txt" in result.output
        assert "test_dir/.hidden_included.txt" not in result.output
        assert "single_file.txt" in result.output
        assert "Contents of single file" in result.output
        result = runner.invoke(
            cli,
            ["test_dir", "single_file.txt", "--ignore-gitignore", "--include-hidden"],
        )
        assert result.exit_code == 0
        assert "test_dir/ignored_in_gitignore.txt" in result.output
        assert "test_dir/.hidden_ignored_in_gitignore.txt" in result.output
        assert "test_dir/included.txt" in result.output
        assert "test_dir/.hidden_included.txt" in result.output
        assert "single_file.txt" in result.output
        assert "Contents of single file" in result.output


def test_binary_file_warning(tmpdir):
    runner = CliRunner(mix_stderr=False)
    with tmpdir.as_cwd():
        os.makedirs("test_dir")
        with open("test_dir/binary_file.bin", "wb") as f:
            f.write(b"\xff")
        with open("test_dir/text_file.txt", "w") as f:
            f.write("This is a text file")
        result = runner.invoke(cli, ["test_dir"])
        assert result.exit_code == 0
        stdout = result.stdout
        stderr = result.stderr
        assert "test_dir/text_file.txt" in stdout
        assert "This is a text file" in stdout
        assert "\ntest_dir/binary_file.bin" not in stdout
        assert (
            "Warning: Skipping file test_dir/binary_file.bin due to UnicodeDecodeError"
            in stderr
        )


def test_template_functionality(tmpdir):
    runner = CliRunner()
    with tmpdir.as_cwd():
        os.makedirs("test_dir")
        with open("test_dir/file1.txt", "w") as f:
            f.write("Content of file1")
        with open("template.txt", "w") as f:
            f.write("File {{index}}: {{path}}\n---\n{{content}}\n---\n")
        result = runner.invoke(cli, ["test_dir", "--template-file", "template.txt"])
        assert result.exit_code == 0
        assert "File 1: test_dir/file1.txt" in result.output
        assert "Content of file1" in result.output


def test_template_with_multiple_files(tmpdir):
    runner = CliRunner()
    with tmpdir.as_cwd():
        os.makedirs("test_dir")
        with open("test_dir/file1.txt", "w") as f:
            f.write("Content of file1")
        with open("test_dir/file2.txt", "w") as f:
            f.write("Content of file2")
        with open("template.txt", "w") as f:
            f.write("File {{index}}: {{path}}\n---\n{{content}}\n---\n")
        result = runner.invoke(cli, ["test_dir", "--template-file", "template.txt"])
        assert result.exit_code == 0
        assert "File 1: test_dir/file1.txt" in result.output
        assert "Content of file1" in result.output
        assert "File 2: test_dir/file2.txt" in result.output
        assert "Content of file2" in result.output


def test_custom_ignore_file(tmpdir):
    runner = CliRunner()
    with tmpdir.as_cwd():
        os.makedirs("test_dir")
        # Files to be ignored by custom ignore file
        with open("test_dir/custom_ignored.txt", "w") as f:
            f.write("This file should be ignored by custom ignore file")
        with open("test_dir/another_custom_ignored.txt", "w") as f:
            f.write("This file should also be ignored by custom ignore file")
        # File to be included
        with open("test_dir/included.txt", "w") as f:
            f.write("This file should be included")

        # Create the custom ignore file
        with open("custom_ignore.txt", "w") as f:
            f.write("custom_ignored.txt\nanother_custom_ignored.txt")

        # Test with custom ignore file
        result = runner.invoke(
            cli, ["test_dir", "--add-ignore-file", "custom_ignore.txt"]
        )
        assert result.exit_code == 0
        assert "test_dir/custom_ignored.txt" not in result.output
        assert "test_dir/another_custom_ignored.txt" not in result.output
        assert "test_dir/included.txt" in result.output


def test_custom_ignore_file_and_gitignore(tmpdir):
    runner = CliRunner()
    with tmpdir.as_cwd():
        os.makedirs("test_dir")
        # File ignored by .gitignore
        with open("test_dir/.gitignore", "w") as f:
            f.write("gitignored.txt")
        with open("test_dir/gitignored.txt", "w") as f:
            f.write("This file should be ignored by .gitignore")

        # File ignored by custom ignore file
        with open("test_dir/custom_ignored.txt", "w") as f:
            f.write("This file should be ignored by custom ignore file")

        # File to be included
        with open("test_dir/included.txt", "w") as f:
            f.write("This file should be included")

        # Create the custom ignore file
        with open("custom_ignore.txt", "w") as f:
            f.write("custom_ignored.txt")

        # Test with both custom ignore file and .gitignore
        result = runner.invoke(
            cli, ["test_dir", "--add-ignore-file", "custom_ignore.txt"]
        )
        assert result.exit_code == 0
        assert "test_dir/gitignored.txt" not in result.output
        assert "test_dir/custom_ignored.txt" not in result.output
        assert "test_dir/included.txt" in result.output


def test_multiple_custom_ignore_files(tmpdir):
    runner = CliRunner()
    with tmpdir.as_cwd():
        os.makedirs("test_dir")
        # Files to be ignored by different custom ignore files
        with open("test_dir/custom_ignored_1.txt", "w") as f:
            f.write("This file should be ignored by custom_ignore_1.txt")
        with open("test_dir/custom_ignored_2.txt", "w") as f:
            f.write("This file should be ignored by custom_ignore_2.txt")

        # File to be included
        with open("test_dir/included.txt", "w") as f:
            f.write("This file should be included")

        # Create the custom ignore files
        with open("custom_ignore_1.txt", "w") as f:
            f.write("custom_ignored_1.txt")
        with open("custom_ignore_2.txt", "w") as f:
            f.write("custom_ignored_2.txt")

        # Test with multiple custom ignore files
        result = runner.invoke(
            cli,
            [
                "test_dir",
                "--add-ignore-file",
                "custom_ignore_1.txt",
                "--add-ignore-file",
                "custom_ignore_2.txt",
            ],
        )
        assert result.exit_code == 0
        assert "test_dir/custom_ignored_1.txt" not in result.output
        assert "test_dir/custom_ignored_2.txt" not in result.output
        assert "test_dir/included.txt" in result.output
