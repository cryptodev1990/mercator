import Head from "next/head";
import { useEffect } from "react";
import type { AppProps } from "next/app";
import Navbar from "../components/navbar";

import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import "../styles/globals.css";

export default function App({ Component, pageProps }: AppProps) {
  useEffect(() => {
    const use = async () => {
      // @ts-ignore `tw-elements` package has no types available
      (await import("tw-elements")).default;
    };
    use();
  }, []);
  return (
    <>
      <Head>
        <title>dubo Analytics</title>
        <meta name="description" content="Analytics made easy" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <Navbar />
      <div className="pr-8 pl-8 pt-8 pb-16 min-h-full">
        <Component {...pageProps} />
      </div>
    </>
  );
}
