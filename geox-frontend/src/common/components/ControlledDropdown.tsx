import { BiCaretDown, BiCaretUp } from "react-icons/bi";
import clsx from "clsx";
import { useState } from "react";

const ControlledDropdown = ({
  options,
  handleOptionSelect,
  selectedOption,
}: any) => {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  const handleDropdownClick = () => {
    setIsDropdownOpen(!isDropdownOpen);
  };

  return (
    <div>
      <div
        className="flex border p-1 rounded items-center w-24"
        onClick={handleDropdownClick}
      >
        {isDropdownOpen ? (
          <BiCaretUp className="fill-black" />
        ) : (
          <BiCaretDown className="fill-black" />
        )}
        <p
          className={clsx({
            ["text-black text-sm"]: true,
          })}
        >
          {selectedOption.label || "Select Format"}{" "}
        </p>
      </div>
      {isDropdownOpen && (
        <div className="absolute bg-white rounded-md shadow-md w-24">
          {options.map((option: { key: string; label: string }) => (
            <div
              className="flex flex-row items-center justify-start w-full h-8 rounded-md cursor-pointer hover:bg-gray-200 p-2"
              onClick={() => {
                handleOptionSelect(option);
                handleDropdownClick();
              }}
            >
              <p className="text-black text-sm">{option.label}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ControlledDropdown;
