import pytest
import jinja2 as j2

from app.core.jinja_utils import ENV, squote

@pytest.mark.parametrize("text,expected", [
    ("Hello 'World'","'Hello \\'World\\''"),
    ("'''", "'\\'\\'\\''"),
])
def test_squote(text: str, expected: str) -> None:
    """Test that squote works as expected."""
    assert squote(text) == expected


def test_squote_filter() -> None:
    """Test that the squote filter works."""
    assert ENV.from_string("{{ \"Hello 'World\" | squote }}").render() == r"'Hello \'World'"


@pytest.mark.parametrize("text,expected", [
    ('Hello "World"','"Hello \\"World\\"'),
])
def test_dquote(text: str, expected: str) -> None:
    """Test that dquote works as expected."""
    assert squote(text) == expected


def test_dquote_filter() -> None:
    """Test that the dquote filter works."""
    assert ENV.from_string("{{ \"Hello \"World\" | dquote }}").render() == r"'Hello \"World'"



def test_undefined_error() -> None:
    """Test that undefined error is raised by a template if a variable is not defined."""
    with pytest.raises(j2.UndefinedError):
        ENV.from_string("{{ asdf }}").render()
