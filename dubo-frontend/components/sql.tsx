import { format } from "sql-formatter";
import SyntaxHighlighter from "react-syntax-highlighter";
import {
  // @ts-ignore
  stackoverflowDark,
  // @ts-ignore
  stackoverflowLight,
} from "react-syntax-highlighter/dist/cjs/styles/hljs";

const SQL = ({
  query,
  light,
  className,
}: {
  query: string;
  light: boolean;
  className?: string;
}) => {
  if (!query) return null;
  return (
    <SyntaxHighlighter
      language="sql"
      style={light ? stackoverflowLight : stackoverflowDark}
      className={className}
    >
      {format(query)}
    </SyntaxHighlighter>
  );
};

export default SQL;
