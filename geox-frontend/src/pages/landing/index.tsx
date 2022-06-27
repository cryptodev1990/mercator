import { Navbar } from "../../components/navbar";

import { GeoJsonLayer } from "@deck.gl/layers";
import { GlobeView } from "./globe-view";
import DeckGL from "@deck.gl/react";
import { useEffect, useState } from "react";

const countries =
  "https://d2ad6b4ur7yvpq.cloudfront.net/naturalearth-3.3.0/ne_50m_admin_0_scale_rank.geojson";

const Globe = () => {
  const [initialViewState, setInitialViewState] = useState({
    longitude: 2.27,
    latitude: 48.86,
    zoom: 0,
    minZoom: 0,
    maxZoom: 0,
  });

  useEffect(() => {
    const intervalId = setInterval(() => {
      setInitialViewState({
        ...initialViewState,
        longitude: initialViewState.longitude + 0.5,
      });
    }, 50);

    return () => {
      clearInterval(intervalId);
    };
  }, [initialViewState]);

  return (
    <DeckGL
      initialViewState={initialViewState}
      controller={false}
      parameters={{ cull: true }}
      layers={[
        new GeoJsonLayer({
          data: countries,
          getLineColor: [255, 255, 255],
          getFillColor: [255, 255, 255],
          stroked: false,
          filled: true,
        }),
      ]}
      views={[new GlobeView()]}
    ></DeckGL>
  );
};

const LandingPage = () => {
  return (
    <main
      className="max-w-full h-screen bg-gradient-to-br from-chestnut-rose to-ublue"
      role="main"
    >
      <section className="">
        <Navbar />
        <div className="grid lg:grid-cols-2 grid-rows-2 gap-10 items-baseline container mx-auto px-4 sm:px-6 lg:px-8 pt-9 pb-20 md:pt-16 md:pb-28 lg:pt-24 lg:pb-36 xl:pt-40 xl:pb-48 text-white">
          <div className="relative max-w-none xl:max-w-md">
            <h1 className="font-heading mb-5 text-4xl leading-tight lg:leading-tight xl:text-5xl xl:leading-tight">
              <strong className="text-white bg-opacity-30 p-2 rounded pl-0 pr-0">
                Mapping software
              </strong>
              <br />
              for data science and operations
            </h1>
            <p className="text-base lg:text-lg xl:text-xl text-white-200 mb-9">
              A suite of geoanalytics tools inspired by the best tooling from
              companies like Uber, Airbnb, and Instacart.
            </p>
            <a
              href="mailto:founders@mercator.tech"
              className="w-full button-xl font-bold bg-white text-ublue text-bold hover:bg-opacity-75 hover:text-porsche transition-colors p-3 rounded"
            >
              Request early access
            </a>
          </div>
          <div className="relative md:h-[160%] xl:h-[110%] h-[230%] hidden sm:block">
            <Globe />
          </div>
        </div>
      </section>
    </main>
  );
};

export default LandingPage;
