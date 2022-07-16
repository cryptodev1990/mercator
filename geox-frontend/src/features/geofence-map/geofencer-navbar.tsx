import { NamespaceListBox } from "./namespace-list-box";
import { ToolButtonBank } from "./tool-button-bank/component";
import Dropdown from "../../common/components/dropdown";
import smallLogo from "../../common/assets/small-logo.svg";

const GeofencerNavbar = () => {
  const css =
    "z-10 flex items-center justify-between font-semibold text-sm text-white";
  return (
    <div>
      <header className={css}>
        <nav
          aria-label="Logo menu"
          className="relative flex flex-row fit-content items-center"
        >
          <a href="/dashboard">
            <img src={smallLogo} alt="logo" className="h-10" />
          </a>
          <p className="ml-3 font-extrabold text-lg">GEOFENCER</p>
        </nav>
        <nav
          aria-label="Main menu"
          className="grid grid-flow-col gap-5 items-center"
        >
          <NamespaceListBox />
          <Dropdown />
        </nav>
      </header>
      <div className="absolute top-[100px] z-30 mx-5 right-0">
        <ToolButtonBank />
      </div>
    </div>
  );
};

export { GeofencerNavbar };
