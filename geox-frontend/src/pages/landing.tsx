import { Navbar } from "../components/navbar";

const LandingPage = () => {
  return (
    <main
      className="max-w-full h-screen bg-gradient-to-br from-chestnut-rose to-ublue"
      role="main"
    >
      <section className="">
        <Navbar />
        <div className="grid lg:grid-cols-2 gap-10 items-baseline container mx-auto px-4 sm:px-6 lg:px-8 pt-9 pb-20 md:pt-16 md:pb-28 lg:pt-24 lg:pb-36 xl:pt-40 xl:pb-48 text-white">
          <div className="relative max-w-none xl:max-w-md">
            <h1 className="font-heading mb-5 text-4xl leading-tight lg:leading-tight xl:text-5xl xl:leading-tight">
              <strong className="text-white bg-chestnut-rose bg-opacity-30 p-2 rounded">
                Mapping software
              </strong>
              <br />
              for operations and data science
            </h1>
            <p className="text-base lg:text-lg xl:text-xl text-white-200 mb-9">
              A suite of geoanalytics tools inspired by the best tooling from
              companies like Uber, Airbnb, and Instacart.
            </p>
            <a
              href="mailto:founders@mercator.tech"
              className="w-full w-auto button-xl font-bold bg-white text-ublue text-bold hover:bg-opacity-75 hover:text-porsche transition-colors p-3 rounded"
            >
              Request early access
            </a>
          </div>
          <div></div>
        </div>
      </section>
    </main>
  );
};

export default LandingPage;
