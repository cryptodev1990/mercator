import { BiBug } from "react-icons/bi";
import smallLogo from "../../common/assets/small-logo-white.svg";
import { useUiModals } from "./hooks/use-ui-modals";
import { UIModalEnum } from "./types";

const GeofencerNavbar = () => {
  const { openModal } = useUiModals();
  return (
    <div
      aria-label="Logo menu"
      className="relative flex flex-row w-full fit-content py-3 px-4"
    >
      <div className="flex flex-row w-full justify-start">
        <div className="self-center">
          <a href="/dashboard">
            <img src={smallLogo} alt="logo" className="h-5" />
          </a>
        </div>
        <div className="ml-1 w-fit pb-2.5 relative">
          <span className="absolute uppercase bottom-0 text-2xs left-0">
            By{" "}
            <a href="/" className="text-porsche">
              Mercator
            </a>
          </span>
          <p className="font-extrabold text-sm">GEOFENCER</p>
        </div>
      </div>
      <div>
        <button
          title="Report a bug or request a feature"
          className="link text-white hover:text-blue-300 border-none hover:border-none"
          onClick={() => openModal(UIModalEnum.SupportModal)}
        >
          <BiBug className="float-right" />
        </button>
      </div>
    </div>
  );
};

export { GeofencerNavbar };
