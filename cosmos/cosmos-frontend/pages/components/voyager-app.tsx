import Image from "next/image";
import { useContext, useEffect } from "react";
import { SearchContext } from "../features/search/context";
import SearchContextProvider from "../features/search/context";
import Header from "./header";
import SearchBar from "./search-bar/search-bar";
import SearchSuggestions from "./search-suggestions";

const ContextProviderNest = ({
  contextProviders,
  children,
}: {
  contextProviders: any[];
  children: React.ReactNode;
}) => {
  for (let i = contextProviders.length - 1; i >= 0; i--) {
    const ContextProvider = contextProviders[i];
    children = <ContextProvider>{children}</ContextProvider>;
  }
  return <>{children}</>;
};

const MainView = () => {
  const { queryPreview, searchText } = useContext(SearchContext);

  if (queryPreview || searchText) {
    return (
      <main className="">
        <header className="relative m-10 select-none">
          <h1 className="absolute text-md">Voyager</h1>
          <Image
            src="/small-star.svg"
            alt="Star"
            width={100}
            height={100}
          ></Image>
        </header>
        <section className="z-10 m-10">
          <SearchBar />
        </section>
      </main>
    );
  }
  return (
    <div className="flex flex-col items-center justify-center min-h-screen py-2">
      <main>
        <section className="20vh">
          <Header />
        </section>
        <section className="z-10">
          <SearchBar />
          <br />
          <SearchSuggestions />
        </section>
      </main>
    </div>
  );
};

const VoyagerApp = () => {
  // first context provider is the outermost
  const providers = [SearchContextProvider];
  return (
    <ContextProviderNest contextProviders={providers}>
      <MainView />
      <Footer />
    </ContextProviderNest>
  );
};

const Footer = () => {
  return (
    <footer className="fixed bottom-0 p-10 bg-[#121212]">
      <span className="p-1">Powered by</span>
      <span className="p-1">
        <a href="https://mercator.tech">Mercator</a>
      </span>
      <span className="p-1">•</span>
      <span className="p-1">
        <a href="https://openstreetmap.org">OpenStreetMap</a>
      </span>
      <span className="p-1">•</span>
      <span className="p-1">
        <a href="https://vis.gl">Vis.gl</a>
      </span>
      <br />
    </footer>
  );
};

export default VoyagerApp;
