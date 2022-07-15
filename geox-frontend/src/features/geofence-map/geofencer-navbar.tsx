import { NamespaceListBox } from "./namespace-list-box";
import { ToolButtonBank } from "./tool-button-bank/component";
import { BsFillGearFill } from "react-icons/bs";

const FENCE_EMOJI = "🏔";

const GeofencerNavbar = () => {
  const css =
    "relative z-10 container mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between font-semibold text-sm text-white";
  return (
    <div>
      <header className={css}>
        <nav aria-label="Logo menu" className="relative z-50 flex ">
          <div>
            <a href="/dashboard">
              <strong>Geofencer</strong>
              {FENCE_EMOJI}
            </a>
          </div>
        </nav>
        <nav
          aria-label="Main menu"
          className="grid grid-flow-col gap-5 items-center"
        >
          <NamespaceListBox />
          <button
            className="transition ease-in-out delay-150 bg-transparent hover:-translate-1 hover:rotate-180 hover:text-porsche duration-300"
            data-tip="Settings"
          >
            <BsFillGearFill size={23} />
          </button>
        </nav>
      </header>
      <div className="absolute top-[100px] z-50 mx-5 right-0">
        <ToolButtonBank />
      </div>
    </div>
  );
};

export { GeofencerNavbar };
