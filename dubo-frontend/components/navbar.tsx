import Link from "next/link";
import DiscordBar from "./discord-bar";

const Navitem = ({ children }: { children: React.ReactNode }) => {
  return (
    <div className="flex flex-row items-center justify-center w-1/3 h-full space-x-3">
      {children}
    </div>
  );
};

const NavbarContainer = ({ children }: { children: React.ReactNode }) => {
  return (
    <div className="h-16 bg-white w-full border-spBlue border-b">
      <div className="flex flex-row h-full justify-between max-w-5xl m-auto text-spBlue">
        {children}
      </div>
    </div>
  );
};

const Navbar = () => {
  return (
    <div>
      {/* <div className="pointer-events-none absolute left-0 top-0 w-[60px] h-full border-r-4 border-r-spBlue"></div>
      <div className="pointer-events-none absolute right-0 top-0 w-[60px] h-full border-l-4 border-l-spBlue"></div>
      <div className="pointer-events-none absolute left-0 bottom-0 w-full h-[60px] border-t-4 border-t-spBlue"></div> */}
      <NavbarContainer>
        <Navitem>
          <Link href={"/"}>
            <div className="text-2xl font-bold ">dubo</div>
          </Link>
        </Navitem>
        <Navitem>
          <Link href={"/pricing"} className="text-lg ">
            Pricing
          </Link>
          <Link href={"/faq"} className="text-lg ">
            About
          </Link>
        </Navitem>
      </NavbarContainer>
      <DiscordBar />
    </div>
  );
};

export default Navbar;
