import { useEffect, useRef, useState } from "react";

const EditableLabel = ({
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
          className="bg-transparent border-b border-gray-500 w-full focus:outline-none focus:border-gray"
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
          className="
          text-white-500
          hover:text-gray-700
          cursor-pointer
          select-none
          overflow-hidden
          max-w-[1/2] truncate
          text-ellipsis"
          onClick={() => setEditing(true)}
        >
          {value || placeholder}
        </div>
      )}
    </div>
  );
};

export default EditableLabel;
