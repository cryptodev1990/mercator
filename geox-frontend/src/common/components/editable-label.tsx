import { useEffect, useRef, useState } from "react";

export const EditableLabel = ({
  value,
  onChange,
  className,
  placeholder,
  disabled,
  ...props
}: {
  value: string;
  onChange: (value: string) => void;
  className?: string;
  placeholder?: string;
  disabled?: boolean;
}) => {
  const [editing, setEditing] = useState(false);
  const [inputValue, setInputValue] = useState(value);

  const inputRef = useRef<HTMLInputElement>(null);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      setEditing(false);
      onChange(inputValue);
    }
  };

  const handleBlur = () => {
    setEditing(false);
    onChange(inputValue);
  };

  useEffect(() => {
    if (editing) {
      inputRef.current?.focus();
    }
  }, [editing]);

  return (
    <div className={className}>
      {editing ? (
        <input
          ref={inputRef}
          className="bg-transparent border-b border-gray-500 w-full text-blue-100"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          onBlur={handleBlur}
          placeholder={placeholder}
          disabled={disabled}
          {...props}
        />
      ) : (
        <div
          className="text-white-500 hover:text-gray-700 cursor-pointer select-none"
          onClick={() => setEditing(true)}
        >
          {value || placeholder}
        </div>
      )}
    </div>
  );
};
