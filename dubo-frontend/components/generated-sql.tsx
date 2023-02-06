import { format } from "sql-formatter";
import SyntaxHighlighter from "react-syntax-highlighter";

import "highlight.js/styles/stackoverflow-light.css";

const GeneratedSQL = ({ query }: { query: string }) => (
  <div className="mt-6 animate-fadeIn100">
    <p className="text-lg">Generated SQL:</p>
    <div className="max-w-5xl mt-2">
      <SyntaxHighlighter useInlineStyles={false} language="sql">
        {format(query)}
      </SyntaxHighlighter>
    </div>
  </div>
);

export default GeneratedSQL;
