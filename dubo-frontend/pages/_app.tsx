import Head from "next/head";
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
  return (
    <>
      <Head>
        <title>dubo Analytics</title>
        <meta name="description" content="Analytics made easy" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <Component {...pageProps} />
    </>
  );
}
