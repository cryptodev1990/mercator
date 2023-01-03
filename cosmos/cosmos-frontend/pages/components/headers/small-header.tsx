import Image from "next/image";
import { useDispatch } from "react-redux";
import { clearSearchResults } from "src/search/search-slice";

const SmallHeader = () => {
  const dispatch = useDispatch();
  return (
    <header
      className="relative select-none cursor-pointer"
      onClick={() => {
        dispatch(clearSearchResults());
      }}
    >
      <h1 className="absolute text-md">Voyager</h1>
      <Image src="/small-star.svg" alt="Star" width={100} height={100}></Image>
    </header>
  );
};

export default SmallHeader;
