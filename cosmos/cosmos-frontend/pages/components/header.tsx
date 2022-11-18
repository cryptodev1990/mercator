import Image from "next/image";
const Header = () => {
  return (
    <div className="my-5 relative h-[100px]">
      <div>
        <h1 className="text-6xl z-30">Voyager</h1>
        {/* import an svg into the nextjs project */}
        <sub className="text-xl z-10">
          The analytical location search engine
        </sub>
      </div>
      <Image
        alt="Voyager logo"
        className="transition-opacity absolute -z-0 translate-x-[30vw] translate-y-[-200px] fade-in"
        src="/shooting-stars.svg"
        width={500}
        height={500}
      />
    </div>
  );
};

export default Header;
