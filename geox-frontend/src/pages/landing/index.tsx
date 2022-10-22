import { useAuth0 } from "@auth0/auth0-react";
import { useNavigate } from "react-router-dom";

import { useEffect } from "react";

import { Navbar } from "../../common/components/navbar";
import { EmailBox } from "./components/email-box";
import { FooterSection } from "./components/footer-section";
import { GradientHeader } from "./components/gradient-header";

import { HeroSection } from "./components/hero-section";
import { ProductSection } from "./components/product-section";

const LandingPage = (): JSX.Element | null => {
  const { isAuthenticated, isLoading } = useAuth0();
  const navigate = useNavigate();

  useEffect(() => {
    if (isAuthenticated) navigate("/dashboard");
  }, [isAuthenticated, navigate]);

  if (isLoading) return null;

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
            <div className="max-w-5xl mx-auto py-5 flex items-center sm:flex-row flex-col gap-3 sm:gap-0">
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
