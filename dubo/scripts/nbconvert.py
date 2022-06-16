import argparse
import jinja2 as j2
import json
import requests
import markdown


from pathlib import Path

import ast

from dataclasses import dataclass


@dataclass
class Import:
    module: str = None
    name: str = None
    alias: str = None


def get_imports(code):
    root = ast.parse(code)

    for node in ast.iter_child_nodes(root):
        if isinstance(node, ast.Import):
            module = []
        elif isinstance(node, ast.ImportFrom):
            module = node.module.split('.')
        else:
            continue

        for n in node.names:
            yield Import(module, n.name, n.asname)


def markdown_to_html(md):
    return markdown.markdown(md)


def code_to_html(code):
    return f'<py-script>\n{code}\n</py-script>'


def json_convert(raw_page):
    parsed = json.loads(raw_page, strict=False)
    html_chunks = []
    imports = []
    output_str = ''
    for c in parsed["cells"]:
        if c["cell_type"] == 'markdown':
            html_chunks.append(markdown_to_html('\n'.join(c['source'])))
        elif c["cell_type"] == 'code':
            code_block = '\n'.join(c['source'])
            imports.extend(get_imports(code_block))
            html_chunks.append(code_to_html(code_block))
    if imports:
        output_str += '<py-env>\n'
        output_str += '\n'.join([x.module or x.name for x in imports])
        output_str += '</py-env>\n'
    output_str += '\n'.join(html_chunks)
    return output_str


def add_body(html_body):
    return j2.Template('''
        <html>
          <head>
            <link rel="stylesheet" href="https://pyscript.net/alpha/pyscript.css" />
             <script defer src="https://pyscript.net/alpha/pyscript.js"></script>
             <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.3.1/dist/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous"/>
          </head>
          <body>
            {{ html_body }}
          </body>
        </html>
        ''').render(html_body=html_body)


def main(args):
    output_text  = ""
    filename = args.filename
    output_fname = filename
    if filename.startswith('https://') and filename.endswith('.ipynb'):
        output_text = json_convert(requests.get(filename).text)
        output_fname = filename.rsplit('/', 1)[-1]
    else:
        with open(args.filename) as f:
            output_text = json_convert(f.read())

    output_text = add_body(output_text)
    with open(Path(output_fname).stem + '.html', 'w+') as f:
        f.write(output_text)

parser = argparse.ArgumentParser(description="Converts a .ipynb to a .html pyscript file")

parser.add_argument("-v", "--verbose", action="store_true")
parser.add_argument("-q", "--quiet", action="store_true")
parser.add_argument("filename", type=str, help="The file to process")

args = parser.parse_args()


if __name__ == "__main__":
    main(args)
