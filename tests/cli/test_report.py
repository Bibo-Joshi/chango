#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT

from pathlib import Path

import pytest
from click import UsageError

from chango.constants import MarkupLanguage
from tests.cli.conftest import ReuseCliRunner


class TestReport:
    @pytest.mark.parametrize(
        "markup",
        [MarkupLanguage.MARKDOWN, MarkupLanguage.HTML, None],
        ids=["Markdown", "HTML", "DefaultMarkup"],
    )
    @pytest.mark.parametrize(
        "markup_option", ["--markup", "-m"], ids=["LongMarkup", "ShortMarkup"]
    )
    @pytest.mark.parametrize(
        ("output", "output_option"), [(None, None), (True, "--output"), (True, "-o")]
    )
    def test_report_version(
        self,
        cli: ReuseCliRunner,
        mock_chango_instance,
        markup,
        markup_option,
        output,
        output_option,
        tmp_path: Path,
    ):
        file_path = tmp_path / "output_file"
        version_note = mock_chango_instance.load_version_note.return_value
        version_note.render.return_value = "expected_render_output"

        args = ["report", "version", "--uid", "1.2.3"]
        if markup is not None:
            args.extend([markup_option, markup.value])
        if output is True:
            args.extend([output_option, file_path.as_posix()])

        result = cli.invoke(args=args)

        assert result.check_exit_code()

        if output is not None:
            assert result.stdout == f"Report written to {file_path}\n"
        else:
            assert result.stdout == "expected_render_output\n"

        mock_chango_instance.load_version_note.assert_called_once_with("1.2.3")
        version_note.render.assert_called_once_with(markup=markup or MarkupLanguage.MARKDOWN)
        if output is True:
            assert file_path.read_text() == "expected_render_output"

    @pytest.mark.parametrize(
        "markup",
        [MarkupLanguage.MARKDOWN, MarkupLanguage.HTML, None],
        ids=["Markdown", "HTML", "DefaultMarkup"],
    )
    @pytest.mark.parametrize(
        "markup_option", ["--markup", "-m"], ids=["LongMarkup", "ShortMarkup"]
    )
    @pytest.mark.parametrize(
        ("output", "output_option"), [(None, None), (True, "--output"), (True, "-o")]
    )
    def test_report_history(
        self,
        cli: ReuseCliRunner,
        mock_chango_instance,
        markup,
        markup_option,
        output,
        output_option,
        tmp_path: Path,
    ):
        file_path = tmp_path / "output_file"
        version_history = mock_chango_instance.load_version_history.return_value
        version_history.render.return_value = "expected_render_output"

        args = ["report", "history"]
        if markup is not None:
            args.extend([markup_option, markup.value])
        if output is True:
            args.extend([output_option, file_path.as_posix()])

        result = cli.invoke(args=args)

        assert result.check_exit_code()

        if output is not None:
            assert result.stdout == f"Report written to {file_path}\n"
        else:
            assert result.stdout == "expected_render_output\n"

        mock_chango_instance.load_version_history.assert_called_once_with()
        version_history.render.assert_called_once_with(markup=markup or MarkupLanguage.MARKDOWN)
        if output is True:
            assert file_path.read_text() == "expected_render_output"

    @pytest.mark.parametrize("invalidity_type", ["dir", "non_writable"])
    @pytest.mark.parametrize("subcommand", ["version", "history"], ids=["Version", "History"])
    def test_report_invalid_file(
        self,
        cli: ReuseCliRunner,
        mock_chango_instance,
        tmp_path: Path,
        invalidity_type,
        subcommand,
    ):
        file_path = tmp_path / "output_file"
        if invalidity_type == "dir":
            output_path = tmp_path
        elif invalidity_type == "non_writable":
            file_path.touch()
            file_path.chmod(0o444)
            output_path = file_path

        args = ["report", subcommand, "--uid", "1.2.3", "--output", output_path.as_posix()]
        result = cli.invoke(args=args)

        assert result.check_exit_code(UsageError.exit_code)
        mock_chango_instance.load_version_note.assert_not_called()

    @pytest.mark.parametrize("subcommand", ["version", "history"], ids=["Version", "History"])
    def test_report_invalid_markup(self, cli: ReuseCliRunner, mock_chango_instance, subcommand):
        args = ["report", subcommand, "--markup", "invalid_markup"]
        if subcommand == "version":
            args.extend(["--uid", "1.2.3"])
        result = cli.invoke(args=args)

        assert result.check_exit_code(UsageError.exit_code)
        mock_chango_instance.load_version_note.assert_not_called()
