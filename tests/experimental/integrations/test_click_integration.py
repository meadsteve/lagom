from unittest import mock

from click.testing import CliRunner

from lagom import Container, injectable
from lagom.experimental.integrations.click import ClickIntegration, ClickIO

container = Container()
cli = ClickIntegration(container)


@cli.command()
@cli.argument("name")
def hello(name, io: ClickIO = injectable):
    io.echo(f"Hello {name}")


def test_click_io_objected_is_injected_and_proxies_click_as_expected():
    runner = CliRunner()
    result = runner.invoke(hello, args=["Steve"])
    assert result.exit_code == 0
    assert result.output == "Hello Steve\n"


def test_a_reference_to_the_plain_function_is_exposed_for_testing():
    mock_io = mock.create_autospec(ClickIO)
    hello.plain_function("again", mock_io)
    mock_io.echo.assert_called_once_with("Hello again")
