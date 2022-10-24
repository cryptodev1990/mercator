import { Container } from "./container";
import { useEffect, useState } from "react";
import { Tab } from "@headlessui/react";
import clsx from "clsx";

type YouTubeVideoProps = {
  video: string;
  title: string;
};
const YouTubeVideo = ({ video, title }: YouTubeVideoProps): JSX.Element => {
  return (
    <iframe
      style={{
        width: "300%",
        border: "none",
        height: "100%",
        marginLeft: "-100%",
      }}
      src={`https://www.youtube.com/embed/${video}?controls=0&modestbranding=1&showinfo=0&rel=0&autoplay=1&loop=1&mute=1&playlist=${video}`}
      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
      title={title}
      frameBorder="0"
    ></iframe>
  );
};

type PrimaryFeatureData = {
  title: string;
  description: string;
  image?: string;
};
const features: PrimaryFeatureData[] = [
  {
    title: "Create",
    description: "Draw or upload your own geofences.",
    image: "6m2Cn02WNuA",
  },
  {
    title: "Edit",
    description: "Split existing geofences or edit their boundaries",
    image: "QxmQuKoFQfE",
  },
  {
    title: "Export",
    description:
      "Send your data to your databases via Snowflake, Redshift, or our developer API",
    image: "oei9-n_5MeI",
  },
];

type AlignTypes = "left" | "right" | "center";

type ProductSectionProps = {
  header: string;
  copytext: string;
  align?: AlignTypes;
  video: string;
};

export const ProductSection = ({
  header,
  copytext,
  align,
  video,
}: ProductSectionProps): JSX.Element => {
  let [tabOrientation, setTabOrientation] = useState("horizontal");

  useEffect(() => {
    let lgMediaQuery: MediaQueryList = window.matchMedia("(min-width: 1024px)");

    function onMediaQueryChange({ matches }: { matches: any }) {
      setTabOrientation(matches ? "vertical" : "horizontal");
    }

    onMediaQueryChange(lgMediaQuery);
    lgMediaQuery.addEventListener("change", onMediaQueryChange);

    return () => {
      lgMediaQuery.removeEventListener("change", onMediaQueryChange);
    };
  }, []);
  return (
    <section
      id="features"
      aria-label="Features for geospaial analysis"
      className="relative overflow-hidden bg-slate-900 pt-20 pb-28 sm:py-32"
    >
      <Container className="relative">
        <div className="max-w-2xl md:mx-auto md:text-center xl:max-w-none">
          <h2 className="font-display text-3xl tracking-tight text-purple-500 sm:text-4xl md:text-5xl">
            Geofencer
          </h2>
          <p className="mt-6 text-lg tracking-tight text-purple-100">
            Draw neighborhood boundaries and create shapes to analyze and report
            on
          </p>
        </div>
        <Tab.Group
          as="div"
          className="mt-16 grid grid-cols-1 items-center gap-y-2 pt-10 sm:gap-y-6 md:mt-20 lg:grid-cols-12 lg:pt-0"
          vertical={tabOrientation === "vertical"}
        >
          {({ selectedIndex }) => (
            <>
              <div className="-mx-4 flex overflow-x-auto pb-4 sm:mx-0 sm:overflow-visible sm:pb-0 lg:col-span-5">
                <Tab.List className="relative z-10 flex gap-x-4 whitespace-nowrap px-4 sm:mx-auto sm:px-0 lg:mx-0 lg:block lg:gap-x-0 lg:gap-y-1 lg:whitespace-normal">
                  {features.map((feature, featureIndex) => (
                    <div
                      key={feature.title}
                      className={clsx(
                        "group relative rounded-xl py-1 px-4 lg:rounded-r-none lg:rounded-l-xl lg:p-6",
                        selectedIndex === featureIndex
                          ? "bg-purple-500 lg:bg-white/10 lg:ring-1 lg:ring-inset lg:ring-white/10"
                          : "hover:bg-white/10 lg:hover:bg-white/5"
                      )}
                    >
                      <h3>
                        <Tab
                          className={clsx(
                            "font-display text-lg [&:not(:focus-visible)]:focus:outline-none",
                            selectedIndex === featureIndex
                              ? "text-white lg:text-purple-500"
                              : "text-purple-100 hover:text-white lg:text-white"
                          )}
                        >
                          <span className="absolute inset-0 rounded-md lg:rounded-r-none lg:rounded-l-md" />
                          {feature.title}
                        </Tab>
                      </h3>
                      <p
                        className={clsx(
                          "mt-2 hidden text-sm lg:block",
                          selectedIndex === featureIndex
                            ? "text-white"
                            : "text-purple-100 group-hover:text-white"
                        )}
                      >
                        {feature.description}
                      </p>
                    </div>
                  ))}
                </Tab.List>
              </div>
              <Tab.Panels className="lg:col-span-7">
                {features.map((feature) => (
                  <Tab.Panel key={feature.title} unmount={false}>
                    <div className="relative sm:px-6 lg:hidden">
                      <div className="absolute -inset-x-4 top-[-6.5rem] bottom-[-4.25rem] bg-white/10 ring-1 ring-inset ring-white/10 sm:inset-x-0 sm:rounded-t-xl" />
                      <p className="relative mx-auto max-w-2xl text-base text-white sm:text-center">
                        {feature.description}
                      </p>
                    </div>
                    {feature.image ? (
                      <div
                        style={{
                          background: "#000",
                          overflow: "hidden",
                          position: "relative",
                          aspectRatio: "16/9",
                          width: "100%",
                          borderRadius: "5px",
                        }}
                      >
                        <YouTubeVideo
                          video={feature.image}
                          title={feature.title}
                        />
                      </div>
                    ) : (
                      <div></div>
                    )}
                  </Tab.Panel>
                ))}
              </Tab.Panels>
            </>
          )}
        </Tab.Group>
      </Container>
    </section>
  );
};
