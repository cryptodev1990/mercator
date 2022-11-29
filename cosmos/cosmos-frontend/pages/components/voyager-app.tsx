import Image from "next/image";
import Header from "./header";
import SearchBar from "./search-bar/search-bar";
import SearchSuggestions from "./search-suggestions";
import { ToastProvider } from "react-toast-notifications";
import GeoMap from "../features/geomap/geomap";
import {
  Provider as ReduxProvider,
  useDispatch,
  useSelector,
} from "react-redux";
import { selectSearchState } from "../../src/search/search-slice";
import LayerCardBar from "./layer-card-bar";
import { wrapper } from "src/store/store";

type ContextType = {
  component: any;
  props?: any;
};

const ContextProviderNest = ({
  contextProviders,
  children,
}: {
  contextProviders: ContextType[];
  children: React.ReactNode;
}) => {
  for (let i = contextProviders.length - 1; i >= 0; i--) {
    const ContextProvider = contextProviders[i];
    children = (
      <ContextProvider.component {...ContextProvider.props}>
        {children}
      </ContextProvider.component>
    );
  }
  return <>{children}</>;
};

const MainView = () => {
  const { inputText, searchResults } = useSelector(selectSearchState);

  if (searchResults.length > 0) {
    return (
      <main className="flex flex-row">
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
        <GeoMap />
        <LayerCardBar />
      </main>
    );
  }

  if (inputText && inputText.length > 0) {
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
        <section className="z-10 m-10 flex flex-col">
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

  const providers = [
    {
      component: ToastProvider,
    },
  ];

  return (
    <ContextProviderNest contextProviders={providers}>
      <MainView />
      <Footer />
    </ContextProviderNest>
  );
};

const Footer = () => {
  return (
    <footer className="fixed bottom-0 p-3 text-sm bg-[#121212] w-full text-center">
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
