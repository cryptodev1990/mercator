"""Utils for jinja2 templates.





"""
import jinja2 as j2
import re

__all__ = ['ENV']

ENV = j2.Environment(loader=j2.PackageLoader('app', 'templates'),
                     undefined=j2.StrictUndefined)
"""A jinja2 environment to use in the rest of the app.

- Provides a jinja2 environment to use in the rest of the app.
- Read templates from app/templates
- Raise error if undefined variable is used
- Adds custom filters

::

    import ENV from app.core.jinja_utils
    ENV.from_string('Hello {{ name }}').render(name='World')

"""

def squote(s: str) -> str:
    """Single quote a string"""
    s = re.sub("'", r"\'", s)
    return f"'{s}'"

ENV.filters["squote"] = squote
