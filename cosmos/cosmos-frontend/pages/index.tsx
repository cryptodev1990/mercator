import Head from "next/head";
import VoyagerApp from "./components/voyager-app";

export default function Home() {
  return (
    <div>
      <Head>
        <title>Voyager -- A Mercator Product</title>
        <meta name="description" content="Generated by create next app" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <VoyagerApp />
    </div>
  );
}
