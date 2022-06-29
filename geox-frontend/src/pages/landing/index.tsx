import { Navbar } from "../../components/navbar";

// @ts-ignore
import { GeoJsonLayer } from "@deck.gl/layers";
import { GlobeView } from "./globe-view";
// @ts-ignore
import DeckGL from "@deck.gl/react";
import { useEffect, useState } from "react";

const countries =
  "https://d2ad6b4ur7yvpq.cloudfront.net/naturalearth-3.3.0/ne_50m_admin_0_scale_rank.geojson";

interface ViewStateArgs {
  longitude: number;
  latitude: number;
  zoom: number;
  minZoom: number;
  maxZoom: number;
}

const Globe = () => {
  const [initialViewState, setInitialViewState] = useState({
    longitude: 2.27,
    latitude: 48.86,
    zoom: 0,
    minZoom: 0,
    maxZoom: 0,
  });

  const [rotate, setRotate] = useState(true);

  useEffect(() => {
    if (!rotate) {
      return;
    }
    const intervalId = setInterval(() => {
      setInitialViewState({
        ...initialViewState,
        longitude: initialViewState.longitude + 0.5,
      });
    }, 50);

    return () => {
      clearInterval(intervalId);
    };
  }, [initialViewState, rotate]);

  return (
    <div onMouseLeave={() => setRotate(true)}>
      <DeckGL
        initialViewState={initialViewState}
        controller={true}
        onDragStart={() => {
          setRotate(false);
        }}
        onDragEnd={(args: any) => {
          const { viewport } = args;
          setInitialViewState({
            ...initialViewState,
            latitude: viewport.latitude,
            longitude: viewport.longitude,
          } as ViewStateArgs);
        }}
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
    </div>
  );
};

const LandingPage = () => {
  return (
    <main
      className="grid grid-flow-row max-w-full h-screen bg-gradient-to-br from-ublue to-chestnut-rose relative overflow-hidden"
      role="main"
    >
      <section className="">
        <Navbar />
        <div className="grid max-w-5xl lg:grid-cols-2 grid-rows-2 gap-10 items-baseline container mx-auto px-4 sm:px-6 lg:px-8 pt-9 md:pt-16 lg:pt-24 xl:pt-40 text-white">
          <div className="relative max-w-none xl:max-w-md">
            <h1 className="font-heading mb-5 text-4xl leading-tight lg:leading-tight xl:text-5xl xl:leading-tight">
              <strong className="text-white">Geospatial analytics</strong>
              <br />
              for data science and operations
            </h1>
            <p className="text-base lg:text-lg xl:text-xl text-white-200 mb-9">
              A suite of tools inspired by the teams from Uber, Airbnb, and
              Instacart.
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
      <section className="relative max-w-5xl container mx-auto px-5 invisible sm:visible flex h-24 font-semibold text-sm text-white">
        <footer className="absolute bottom-0 right-0">
          Copyright © 2022 Mercator HQ
        </footer>
      </section>
    </main>
  );
};

export default LandingPage;
