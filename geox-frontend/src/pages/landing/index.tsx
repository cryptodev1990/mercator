import { useAuth0 } from "@auth0/auth0-react";

import { useEffect, useState } from "react";
import { useNavigate } from "react-router";

import { Navbar } from "../../common/components/navbar";
import { FooterSection } from "./components/footer-section";

import { HeroSection } from "./components/hero-section";
import { ProductSection } from "./components/product-section";

const Triangle = () => (
  <div className="relative rotate-[135deg] animate-pulse">
    <div className="absolute top-0 left-0 w-0 h-0 border-t-[20px] border-l-8 border-white"></div>
    <div className="absolute bottom-0 right-0 w-0 h-0 border-b-8 border-r-[20px] border-white"></div>
    <div className="absolute bottom-0 left-0 w-full h-0 border-b-8 border-l-8 border-white"></div>
  </div>
);

const ScrollDownArrow = ({ hidden, setHidden }: any) => {
  if (hidden) return null;
  return (
    <div
      className="absolute bottom-0 left-1/2 transform -translate-x-1/2 cursor-pointer mb-10"
      onClick={() => {
        window.location.href = "#geofencer-features";
        setHidden(true);
      }}
    >
      <Triangle />
    </div>
  );
};

const LandingPage = (): JSX.Element | null => {
  const { isAuthenticated, isLoading } = useAuth0();
  const navigate = useNavigate();
  const [hidden, setHidden] = useState(false);

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
              <ScrollDownArrow hidden={hidden} setHidden={setHidden} />
            </div>
          </div>
          <ProductSection />
          <div className="max-w-5xl mx-auto py-5 flex items-center sm:flex-row flex-col gap-3 sm:gap-0"></div>
          <FooterSection />
        </div>
      </div>
    </main>
  );
};

export default LandingPage;
