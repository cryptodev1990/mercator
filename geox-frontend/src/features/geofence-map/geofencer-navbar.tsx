import smallLogo from "../../common/assets/small-logo-white.svg";

const GeofencerNavbar = () => {
  return (
    <div
      aria-label="Logo menu"
      className="relative flex flex-row fit-content items-center py-3 px-4"
    >
      <a href="/dashboard">
        <img src={smallLogo} alt="logo" className="h-5" />
      </a>
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
  );
};

export { GeofencerNavbar };
