import Link from "next/link";
import DiscordBar from "./discord-bar";

const Navbar = () => (
  <div>
    <nav className="relative w-full flex flex-wrap items-center justify-center py-4 bg-white border-spBlue border-b">
      <div className="container-fluid w-full flex flex-wrap items-center justify-between px-6 max-w-2xl">
        <div className="flex items-center mr-1">
          <Link href={"/"}>
            <div className="text-2xl text-spBlue font-bold">dubo</div>
          </Link>
        </div>
        <div className="flex items-center relative">
          <Link href={"/faq"} className="text-lg ">
            <div className="text-spBlue">About</div>
          </Link>
        </div>
      </div>
    </nav>
    <DiscordBar />
  </div>
);

export default Navbar;
