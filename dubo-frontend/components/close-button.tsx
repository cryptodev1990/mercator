import { MdClose } from "react-icons/md";

const CloseButton = ({ onClick }: { onClick: () => void }) => (
  <button
    onClick={onClick}
    className="transition hover:-translate-y-1 font-bold py-2 px-4 rounded inline-flex items-center"
  >
    <MdClose />
  </button>
);

export { CloseButton };
