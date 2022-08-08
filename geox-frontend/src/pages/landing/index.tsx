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
      w-screen
      bg-gradient-to-tl from-ublue to-chestnut-rose
      overflow-scroll-none
      fixed"
      role="main"
    >
      <div className="max-w-5xl mx-auto border-b-2 py-5">
        <Navbar />
      </div>
      <div className="relative overflow-y-scroll h-screen snap-y">
        <div className="my-20">
          <HeroSection />
        </div>
        {/* Products */}
        <div className="max-w-5xl mx-auto border-b snap-start">
          <GradientHeader>Our products</GradientHeader>
        </div>
        <ProductSection
          header="Control dispatch, analysis, and reporting with Geofencer"
          video={"PdZAk17Gxx0"}
          copytext={
            "Draw neighborhood boundaries, annotate maps, and create regions to analyze and report on. Publish shapes to web hooks and databases directly or consume via our SDK."
          }
          align="right"
        />
        <ProductSection
          header="Celestial: Track your fleet"
          video={"95shFHRoZZw"}
          copytext={
            "Receive real-time updates on your assets, message your drivers, set up alerts for issues, get analytics on your live and historic data, and support tracking thousands of assets effortlessly."
          }
          align="left"
        />
        <ProductSection
          header="Make your GPS data dependable using our developer API"
          video={"-h58GEoxeoI"}
          copytext={
            "Impute missing GPS data or extrapolate future pings with our GPS APIs. In particular, manage pay for your contractors for Prop 22 in California, even in the presence of damaged or missing GPS."
          }
          align="left"
        />
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
    </main>
  );
};

export default LandingPage;
