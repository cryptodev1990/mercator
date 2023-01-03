import Header from "./headers/header";
import SearchBar from "./bars/search-bar";
import SearchSuggestions from "./search-suggestions";
import { useSelector } from "react-redux";
import { selectSearchState } from "../../src/search/search-slice";
import AnalysisView from "./analysis-view";
import Footer from "./footer";
import ContextProviderNest from "./context-helpers/context-provider-nest";
import SmallHeader from "./headers/small-header";

const MainView = () => {
  const { inputText, searchResults } = useSelector(selectSearchState);

  if (searchResults.length > 0) {
    return <AnalysisView />;
  }

  if (inputText && inputText.length > 0) {
    return (
      <main className="max-w-5xl m-auto flex flex-col justify-center items-center">
        <SmallHeader />
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

  return (
    <ContextProviderNest>
      <FullScreen>
        <MainView />
        <Footer />
      </FullScreen>
    </ContextProviderNest>
  );
};

const FullScreen = ({ children }: { children: React.ReactNode }) => {
  return (
    <div className="w-screen h-screen">
      <div className="w-full h-full">{children}</div>
    </div>
  );
};

export default VoyagerApp;
