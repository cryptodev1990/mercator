/* global window */
import Head from "next/head";
import { useEffect } from "react";
import type { AppProps } from "next/app";
import Navbar from "../components/navbar";
import useDatadogRum from "../lib/hooks/use-datadog-rum";
import useTailwindElements from "../lib/hooks/use-tailwind-elements";

import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import "../styles/globals.css";

import { Roboto } from "@next/font/google";

const roboto = Roboto({
  weight: "400",
  subsets: ["latin"],
});

export default function App({ Component, pageProps, router }: AppProps) {
  useTailwindElements();
  useDatadogRum();

  const head = (
    <Head>
      <title>dubo Analytics</title>
      <meta name="description" content="Analytics made easy" />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <link rel="icon" href="/favicon.ico" />
    </Head>
  );

  const style = (
    <style jsx global>
      {`
        :root {
          --roboto-font: ${roboto.style.fontFamily};
        }
      `}
    </style>
  );

  if (router.pathname.startsWith("/demos/census")) {
    return (
      <main>
        {style}
        {head}
        <Component {...pageProps} />
      </main>
    );
  }
  return (
    <main>
      {style}
      {head}
      <Navbar />
      <div className="pr-8 pl-8 pt-8 pb-16 min-h-full">
        <Component {...pageProps} />
      </div>
    </main>
  );
}
