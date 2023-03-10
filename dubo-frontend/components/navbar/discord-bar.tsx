import { useState } from "react";
import { FaArrowRight, FaDiscord } from "react-icons/fa";

const DISCORD_URL = "https://discord.gg/u2GgjX9eKU";

const DiscordBar = () => {
  const [hidden, setHidden] = useState(false);
  if (hidden) {
    return null;
  }
  return (
    <div className="w-full flex flex-row items-center justify-center bg-spBlue text-white gap-3 p-2">
      <div className="flex flex-row gap-3 items-center">
        <div>
          <FaDiscord size={30} />
        </div>
        <a
          className="items-center justify-center hidden md:flex"
          href={DISCORD_URL}
          rel="noopener noreferrer"
          target="_blank"
        >
          <span>Join dubo on Discord</span>
        </a>
        <button
          onClick={() => {
            // navigate to DISCORD_URL
            window.open(DISCORD_URL, "_blank");
          }}
          className="inline-block px-3 py-2 hover:text-spBlue border border-white hover:bg-white border-spBlue text-white font-medium text-md leading-tight hover:bg-white focus:outline-none focus:ring-0 transition duration-150 ease-in-out"
        >
          <div className="flex flex-row gap-3 items-center">
            <span>Join dubo </span>
            <FaArrowRight size={20} />
          </div>
        </button>
      </div>
      <div
        className="cursor-pointer max-w-10 absolute right-3"
        onClick={() => {
          setHidden(true);
        }}
      >
        <svg
          width="13"
          height="13"
          viewBox="0 0 13 13"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M12.972 11.648 7.736 6.44l5.236-5.208L11.712 0 6.504 5.208 1.296 0 .064 1.232 5.272 6.44.064 11.648l1.232 1.232 5.208-5.208 5.208 5.208 1.26-1.232Z"
            fill="#fff"
          ></path>
        </svg>
      </div>
    </div>
  );
};

export default DiscordBar;
