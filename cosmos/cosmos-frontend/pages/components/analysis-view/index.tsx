import GeoMap from "@/pages/features/geomap/geomap";
import Image from "next/image";
import Link from "next/link";
import { useDispatch } from "react-redux";
import { clearSearchResults } from "src/search/search-slice";
import ErrorBar from "../error-bar";
import LayerCardBar from "../layer-card-bar";
import SearchBar from "../search-bar/search-bar";

const AnalysisView = () => {
  const dispatch = useDispatch();

  return (
    <main className="flex flex-row m-auto w-full gap-1 max-w-[3000px] h-screen overflow-hidden">
      <div className="w-full flex flex-col gap-3">
        <header className="relative mt-10 select-none flex flex-row gap-4">
          <span
            className="ml-5 cursor-pointer"
            onClick={() => {
              dispatch(clearSearchResults());
            }}
          >
            <Link href={"/"}>
              <h1 className="absolute text-md">Voyager</h1>
              <Image
                className="w-30 h-10"
                src="/small-star.svg"
                alt="Star"
                width={100}
                height={100}
              ></Image>
            </Link>
          </span>
          <div className="w-full">
            <SearchBar />
          </div>
          <ErrorBar />
        </header>
        <div className="relative h-full">
          <GeoMap />
        </div>
      </div>
      <div className="h-[100%] mt-10 bg-black-500">
        <LayerCardBar />
      </div>
    </main>
  );
};

export default AnalysisView;
