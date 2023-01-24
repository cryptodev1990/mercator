import { MdClose } from "react-icons/md";

const CloseButton = ({ onClick }: { onClick: () => void }) => {
  return (
    <button
      onClick={onClick}
      className="hover:bg-gray-300 text-gray-800 font-bold py-2 px-4 rounded inline-flex items-center"
    >
      <MdClose />
    </button>
  );
};

export { CloseButton };
