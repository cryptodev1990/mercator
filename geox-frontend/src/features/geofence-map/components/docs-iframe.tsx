import { useContext } from "react";
import { BiHelpCircle } from "react-icons/bi";
import { CancelIcon, NewWindowIcon } from "../../../common/components/icons";
import { UIContext } from "../contexts/ui-context";

const DOCS = "https://pages.mercator.tech/";

export const DocsIframe = () => {
  const { showDocs, setShowDocs } = useContext(UIContext);
  if (!showDocs) return null;
  return (
    <div
      className="bg-white h-screen w-[50vw] z-50
        pl-5 pt-2 translate-y-[-10px]
        translate-x-2 border-l-2 border-black"
    >
      <div className="absolute w-full pr-10">
        <button
          onClick={() => {
            // navigate to docs useImperativeHandle(
            window.open(DOCS, "_blank");
          }}
          className="float-left text-gray-400"
        >
          <NewWindowIcon />
        </button>
        <button
          onClick={() => setShowDocs(!showDocs)}
          className="float-right text-gray-400"
        >
          <CancelIcon size={20} />
        </button>
      </div>
      <iframe title="Geofencer Docs" className="w-full h-full" src={DOCS} />
    </div>
  );
};

export const DocsButton = () => {
  const { showDocs, setShowDocs } = useContext(UIContext);
  return (
    <div className="flex pt-auto">
      <button
        onClick={() => setShowDocs(!showDocs)}
        className="btn btn-circle bg-slate-500 border-none"
      >
        <BiHelpCircle size={21} className="text-white"></BiHelpCircle>
      </button>
    </div>
  );
};
