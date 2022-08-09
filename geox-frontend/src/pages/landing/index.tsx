import { Navbar } from "../../common/components/navbar";
import { EmailBox } from "./email-box";
import { FooterSection } from "./footer-section";
import { GradientHeader } from "./gradient-header";

import { HeroSection } from "./hero-section";
import { ProductSection } from "./product-section";

const LandingPage = () => {
  return (
    <main
      className="
      top-0
      left-0
      bg-slate-900
      w-screen
      overflow-scroll-none
      fixed"
      role="main"
    >
      <div className="">
        <div className="relative overflow-y-scroll h-screen">
          <div className="absolute skew-y-12 h-[100vh] z-0 w-[100vw] -translate-y-40 bg-gradient-to-br from-secondary to-purple-500 overflow-hidden"></div>
          <div className="max-w-5xl mx-auto py-5 h-screen">
            <Navbar />

            <div className="my-12 sm:my-20 container">
              <HeroSection />
            </div>
          </div>
          {/* Products */}
          <div className="z-50 container max-w-5xl mx-auto my-10">
            <div className="">
              <ProductSection
                header="Control dispatch, analysis, and reporting with Geofencer"
                video={"PdZAk17Gxx0"}
                copytext={
                  "Draw neighborhood boundaries and create shapes to analyze and report on"
                }
                align="right"
              />
            </div>
            <div className="relative">
              <ProductSection
                header="Celestial: Track your fleet"
                video={"95shFHRoZZw"}
                copytext={
                  "Receive real-time updates on your assets, message your drivers. Effortlessly track thousands or even tens of thousands of assets."
                }
                align="left"
              />
            </div>
            <div className="relative">
              <ProductSection
                header="Make your GPS data dependable using our developer API"
                video={"-h58GEoxeoI"}
                copytext={
                  "Impute missing GPS data or extrapolate future pings with our GPS APIs. In particular, manage pay for your contractors for Prop 22 in California, even in the presence of damaged or missing GPS."
                }
                align="right"
              />
            </div>
            <div className="max-w-5xl mx-auto py-5 border-b border-t flex items-center sm:flex-row flex-col gap-3 sm:gap-0">
              <div className="flex-1">
                <GradientHeader>Like what you see? Try it out.</GradientHeader>
              </div>
              <div className="sm:w-1/2 w-full sm:p-0 p-5">
                <EmailBox />
              </div>
            </div>
            <FooterSection />
          </div>
        </div>
      </div>
    </main>
  );
};

export default LandingPage;
