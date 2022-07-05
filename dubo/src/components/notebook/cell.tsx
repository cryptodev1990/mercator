import React, { useState } from 'react';

/* @ts-ignore */
import { markdown } from 'markdown';
import { CodeEditor } from './editor';

type Nullable<T> = T | null;

// @ts-ignore
let initPyodide = window.loadPyodide({
  indexURL: 'https://cdn.jsdelivr.net/pyodide/v0.20.0/full/',
  stdout: (text: string) => console.log('GOVERNED', text),
  stderr: (text: string) => console.error(text)
});

async function execPy(code: string): Promise<string> {
  let pyodide = await initPyodide;
  await pyodide.loadPackage('micropip');
  await pyodide.loadPackage(['matplotlib', 'numpy', 'pandas']);
  const result = await pyodide.runPythonAsync(code);
  return result;
}

interface InputCell {
  input: Nullable<string>;
  inputType: CellInputType;
  handleOutput: (output: Nullable<string>) => void;
}

const InputCell = ({ input, inputType, handleOutput }: InputCell) => {
  const [code, setCode] = useState<string>(input || '');
  const [evaluating, setEvaluating] = useState<boolean>(false);

  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === 'Enter' && e.ctrlKey) {
      e.preventDefault();
      setEvaluating(true);
      onRun();
    }
  };

  const onRun = async () => {
    switch (inputType) {
      case CellInputType.Python:
        const result = await execPy(code);
        setEvaluating(false);
        handleOutput(result);
        break;
      case CellInputType.Markdown:
        let html = markdown.toHTML(code) as string;
        setEvaluating(false);
        handleOutput(html);
        break;
      case CellInputType.Html:
        handleOutput(code);
        break;
      case CellInputType.JavaScript:
        alert('Not implemented - check back later');
        break;
    }
  };

  return (
    <>
      <div>
        <label
          htmlFor="message"
          className="block mb-2 text-sm font-medium text-gray-900 dark:text-gray-400">
          Notebook cell (Ctrl+Enter to run) {evaluating ? '...' : ''}
        </label>
        <CodeEditor code={code} setCode={setCode} handleKeyDown={handleKeyDown}></CodeEditor>
      </div>
    </>
  );
};

interface OutputCellProps {
  output?: string;
}

const OutputCell = (props: OutputCellProps) => {
  if (!props.output) {
    return <></>;
  }
  return <div dangerouslySetInnerHTML={{ __html: props.output }}></div>;
};

enum CellInputType {
  Python,
  Markdown,
  Html,
  JavaScript
}

interface NotebookCell {
  input: Nullable<string>;
  inputType: CellInputType;
  output: Nullable<string>;
}

const Cell: React.FC<NotebookCell> = ({ input, inputType, output }) => {
  const [data, setData] = useState<NotebookCell>({
    input: input || '',
    inputType: inputType || CellInputType.Python,
    output: output || ''
  });
  function handleOutput(output: Nullable<string>) {
    setData({ ...data, output });
  }
  return (
    <section>
      <InputCell input={data.input} inputType={data.inputType} handleOutput={handleOutput} />
      <OutputCell output={data.output || ''} />
    </section>
  );
};

const NotebookCells = (props: { cells: NotebookCell[] }) => {
  const [cellList, setCellList] = useState<Array<NotebookCell>>(props.cells);
  if (!cellList) {
    return null;
  }
  let cellComponents: Array<JSX.Element> = [];
  for (const cell of props.cells) {
    cellComponents.push(
      <Cell input={cell.input} inputType={cell.inputType} output={cell.output}></Cell>
    );
  }
  return <main>{cellComponents}</main>;
};

export { InputCell, NotebookCells };
