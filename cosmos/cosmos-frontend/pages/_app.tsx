import "../styles/globals.css";
import type { AppProps } from "next/app";
import { wrapper } from "src/store/store";
import { Provider } from "react-redux";

function App({ Component, ...rest }: AppProps) {
  const { store, props } = wrapper.useWrappedStore(rest);
  return (
    <Provider store={store}>
      <Component {...props.pageProps} />
    </Provider>
  );
}

export default App;
