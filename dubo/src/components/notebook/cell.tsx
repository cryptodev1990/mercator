import React, { useState } from 'react';

// @ts-ignore
let initPyodide = window.loadPyodide({
  indexURL: 'https://cdn.jsdelivr.net/pyodide/v0.20.0/full/'
});

function generateGuid(): string {
  var result, i, j;
  result = '';
  for (j = 0; j < 32; j++) {
    if (j == 8 || j == 12 || j == 16 || j == 20) result = result + '-';
    i = Math.floor(Math.random() * 16)
      .toString(16)
      .toUpperCase();
    result = result + i;
  }
  return result;
}

async function execPy(kw: string, code: string): Promise<string> {
  let pyodide = await initPyodide;
  pyodide.globals.set('mikw', kw);
  await pyodide.loadPackage('micropip');
  await pyodide.loadPackage(['matplotlib', 'numpy', 'pandas']);
  const result = await pyodide.runPythonAsync(code);
  console.log(result);
  return result;
}

const InputCell = () => {
  const [code, setCode] = useState<string>(`
import pandas as pd
# Patch urlopen to work with pyodide
import pyodide
url = "https://raw.githubusercontent.com/selva86/datasets/master/mtcars.csv"
# pd.io.common.urlopen = pyodide.open_url
df = pd.read_csv(pyodide.open_url(url))
df.to_html() 
  `);
  const [output, setOutput] = useState<string>('');
  const [evaluating, setEvaluating] = useState<boolean>(false);

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setCode(e.target.value);
  };

  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === 'Enter' && e.ctrlKey) {
      e.target.style.height = 'inherit';
      e.target.style.height = `${e.target.scrollHeight}px`;

      e.preventDefault();
      setEvaluating(true);
      onRun();
    }
  };

  const onRun = async () => {
    const result = await execPy(generateGuid(), code);
    setEvaluating(false);
    setOutput(result);
  };

  return (
    <>
      <label
        htmlFor="message"
        className="block mb-2 text-sm font-medium text-gray-900 dark:text-gray-400">
        Notebook cell (Ctrl+Enter to run) {evaluating ? '...' : ''}
      </label>
      <textarea
        id="message"
        rows={4}
        value={code}
        onChange={handleChange}
        onKeyDown={handleKeyDown}
        className="block font-mono p-2.5 w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
        placeholder="Your code..."></textarea>
      <OutputCell data={output} />
    </>
  );
};

interface OutputCellProps {
  data?: string;
}

const OutputCell = ({ data }: OutputCellProps) => {
  if (!data) {
    return <></>;
  }
  return <div dangerouslySetInnerHTML={{ __html: data }}></div>;
};

const Cell = () => {
  return (
    <>
      <InputCell></InputCell>
      <OutputCell></OutputCell>
    </>
  );
};

export { InputCell };
