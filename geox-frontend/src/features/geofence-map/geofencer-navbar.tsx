import ReactTooltip from "react-tooltip";
import { useNavigate } from "react-router";
import smallLogo from "../../common/assets/small-logo-white.svg";
import { BsFillGearFill } from "react-icons/bs";
import { useState } from "react";
import { useAuth0 } from "@auth0/auth0-react";

//   {isLoading && (
// <ReactLoading type={"spin"} height={"1rem"} width={"1rem"} />
//   )}

const GeofencerNavbar = () => {
  const nav = useNavigate();
  const [tooltip, showTooltip] = useState(false);
  const { user } = useAuth0();

  const tooltipEvents = {
    onMouseEnter: () => showTooltip(true),
    onMouseLeave: () => {
      showTooltip(false);
      setTimeout(() => showTooltip(true), 50);
    },
  };

  const css =
    "relative z-10 container mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between font-semibold text-sm text-white";
  return (
    <header className={css}>
      <nav aria-label="Logo menu" className="relative z-50 flex ">
        <div data-tip="Back to dashboard" {...tooltipEvents}>
          <a href="/dashboard">
            <img
              src={smallLogo}
              alt="logo"
              className="transition h-10 hover:-translate-1 hover:-rotate-45"
            />
          </a>
        </div>
      </nav>
      <nav aria-label="Main menu" className="grid grid-flow-col gap-5">
        {user && <div>Hello, {user?.email}</div>}
        <button
          className="transition ease-in-out delay-150 bg-transparent hover:-translate-1 hover:rotate-180 hover:text-porsche duration-300"
          data-tip="Settings"
          {...tooltipEvents}
        >
          <BsFillGearFill size={23} />
        </button>
      </nav>

      {tooltip && <ReactTooltip effect="solid" place="right" type="dark" />}
    </header>
  );
};

export { GeofencerNavbar };
