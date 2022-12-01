import Image from "next/image";
import Header from "./header";
import SearchBar from "./search-bar/search-bar";
import SearchSuggestions from "./search-suggestions";
import { ToastProvider } from "react-toast-notifications";
import { useSelector } from "react-redux";
import { selectSearchState } from "../../src/search/search-slice";
import AnalysisView from "./analysis-view";
import ErrorBar from "./error-bar";

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
    return <AnalysisView />;
  }

  if (inputText && inputText.length > 0) {
    return (
      <main className="max-w-5xl m-auto flex flex-col justify-center items-center">
        <header className="relative m-10 select-none flex flex-row min-w-full gap-5">
          <h1 className="absolute text-md">Voyager</h1>
          <Image
            src="/small-star.svg"
            alt="Star"
            width={100}
            height={100}
          ></Image>
          <ErrorBar />
        </header>
        <section className="z-10 w-full">
          <SearchBar />
        </section>
      </main>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-screen py-2">
      <main>
        <section>
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
      <div className="w-screen h-screen">
        <MainView />
      </div>
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
