import { useAuth0 } from "@auth0/auth0-react";
import { useNavigate } from "react-router-dom";

import { useEffect } from "react";

import { Navbar } from "../../common/components/navbar";
import { FooterSection } from "./components/footer-section";

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
        <div className="relative overflow-y-scroll h-screen overflow-x-hidden">
          <div className="absolute skew-y-12 h-screen z-0 w-[100vw] -translate-y-40 bg-gradient-to-br from-secondary to-purple-500 overflow-hidden"></div>
          <div className="max-w-5xl mx-auto py-5 h-screen">
            <Navbar />

            <div className="">
              <HeroSection />
            </div>
          </div>
          {/* Products */}
          <ProductSection
            header="Control dispatch, analysis, and reporting with Geofencer"
            video={"PdZAk17Gxx0"}
            copytext={
              "Draw neighborhood boundaries and create shapes to analyze and report on"
            }
            align="right"
          />
          <div className="max-w-5xl mx-auto py-5 flex items-center sm:flex-row flex-col gap-3 sm:gap-0"></div>
          <FooterSection />
        </div>
      </div>
    </main>
  );
};

export default LandingPage;
