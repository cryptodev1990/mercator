import { useEffect } from "react";
import "../styles/globals.css";
import type { AppProps } from "next/app";

export default function App({ Component, pageProps }: AppProps) {
  useEffect(() => {
    const use = async () => {
      // @ts-ignore `tw-elements` package has no types available
      (await import("tw-elements")).default;
    };
    use();
  }, []);
  return <Component {...pageProps} />;
}
