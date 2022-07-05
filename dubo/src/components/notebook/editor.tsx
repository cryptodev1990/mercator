// https://github.com/suren-atoyan/monaco-react#usemonaco
import Editor from '@monaco-editor/react';

import { useState, useRef } from 'react';

interface EditorProps {
  code: string;
  setCode: (code: string) => void;
  handleKeyDown: any;
}

export function CodeEditor({ code, setCode, handleKeyDown }: EditorProps) {
  const editorRef = useRef(null);
  const [height, setHeight] = useState(50);

  // @ts-ignore
  function handleEditorDidMount(editor, monaco) {
    editorRef.current = editor;
    const contentHeight = editor.getContentHeight();
    setHeight(contentHeight);
  }

  // https://microsoft.github.io/monaco-editor/api/modules/monaco.editor.html#LineNumbersType
  return (
    <div onKeyDown={handleKeyDown}>
      <Editor
        height={height}
        defaultLanguage="python"
        value={code}
        theme="light"
        onMount={handleEditorDidMount}
        defaultValue="Your code here..."
        options={{
          minimap: { enabled: false },
          overviewRulerLanes: 0,
          scrollbar: {
            vertical: 'hidden'
          }
        }}
        onChange={(value, e) => {
          if (editorRef.current) {
            // @ts-ignore
            setCode(editorRef.current.getValue());
            // @ts-ignore
            const contentHeight = editorRef.current.getContentHeight();
            setHeight(contentHeight);
          }
        }}
      />
    </div>
  );
}
