import { NotebookCells } from '../components/notebook/cell';

const PANDAS = `import pandas as pd
# Patch urlopen to work with pyodide
import pyodide
url = "https://raw.githubusercontent.com/selva86/datasets/master/mtcars.csv"
# pd.io.common.urlopen = pyodide.open_url
df = pd.read_csv(pyodide.open_url(url))
df.to_html()`;

const DEMO_CELLS = [
  {
    input: 'print(1)',
    inputType: 0,
    output: '1'
  },
  {
    input: PANDAS,
    inputType: 0,
    output: null
  },
  {
    input: 'print(2)',
    inputType: 0,
    output: '2'
  },
  {
    input: "*Above* we've see how to print a number to the console.",
    inputType: 1,
    output:
      "<p>Above&nbsp;we&nbsp;'ve&nbsp;see&nbsp;how&nbsp;to&nbsp;print&nbsp;a&nbsp;number&nbsp;to&nbsp;the&nbsp;console.</p>"
  },
  {
    input: 'Here I can demonstrate how to use <strong>HTML</strong>',
    inputType: 2,
    output: '3'
  },
  {
    input: "console.log('what about some good old javascript?')",
    inputType: 3,
    output: 'what about some good old javascript?'
  }
];

const NotebookPage = () => {
  return (
    <div>
      <h1>Notebook</h1>
      <NotebookCells cells={DEMO_CELLS} />
    </div>
  );
};

export { NotebookPage };
