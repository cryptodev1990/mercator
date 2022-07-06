Jul 5 2022
----------

### Progress
- Use Monaco Editor, mostly for auto-complete and syntax highlighting

### Plans
- Errors should not catastrophically crash the Python UI. How do I do error handling? Starboard has this figured out.
- Editor height should better fit the number of lines

### Observations
- [CodeMirror](https://uiwjs.github.io/react-codemirror/) might be a lighter weight alternative
- Market has: PyScript, Steamlit, ReTool, Anvil, Iodide (RIP), Pyodide, Jupyter, Starboard

Jul 6 2022
----------

## Plans
- [ ] Try CodeMirror
- [ ] Route stdout and stderr to cell output (See starboard.gg)
- [ ] Just use starboard's pyodide installation?

### Observations
- [Someone wrote a treeshaker](https://pypi.org/project/treeshaker/) for Python code.
  Could we take the treeshaker, apply it to scripts from notebooks, and build a custom library.
  (I tried it locally, currently it does not work.)
- [Python intellisense](https://github.com/microsoft/monaco-editor/issues/421) would be great to have for the IDE
