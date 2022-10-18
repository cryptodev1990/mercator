import { EmailBox } from "./email-box";
import ycLogo from "./yc-logo.png";
import tribeCapitalLogo from "./Tribe_Capital_logo.webp";
import somaLogo from "./Soma_Capital_logo.webp";
import rebelLogo from "./Rebel_Fund_logo.webp";
import amplifyLogo from "./Amplify_Partners_logo.jpeg";
import valorLogo from "./Valor_Equity_Partners_logo.webp";

import { Globe } from "./globe";
import { useEffect, useRef } from "react";
export const InvestorSection = () => {
  const investors = [
    {
      url: "https://www.ycombinator.com/",
      logo: ycLogo,
      text: "Y Combinator",
    },
    {
      url: "https://tribecap.co/",
      logo: tribeCapitalLogo,
      text: "Tribe Capital"
    },
    {
      url: "https://www.rebelfund.vc/",
      logo: rebelLogo,
      text: "Rebel Fund"
    },
    {
      url: "https://www.somacap.com/",
      logo: somaLogo,
      text: "Soma Capital"
    },
    {
      url: "https://www.valorep.com/",
      logo: valorLogo,
      text: "Valor Equity Partners"
    },
    {
      url: "https://amplifypartners.com/",
      logo: amplifyLogo,
      text: "Amplify Partners"
    }

  ];

  return (
    <div className="py5 text-xs font-bold">
      <p className="py-2">Backed by</p>
      <div className="flex flex-row space-x-5">
        {investors.map((investor) => {
          return (
            <div>
              <a
                href={investor.url}
                target="_blank"
                rel="noreferrer"
                className="select-none cursor-default"
                style={{
                  display: "inline-block",
                  height: "60px",
                }}
              >
                <img
                  src={investor.logo}
                  title={investor.text}
                  className="h-[60px] cursor-pointer"
                  alt={investor.text}
                ></img>
              </a>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export const HeroSection = () => {
  const ref = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (ref.current) {
      ref.current.focus();
    }
  }, []);

  return (
    <section ref={ref} className="m-1">
      <div className="grid max-w-5xl md:grid-cols-2 gap-20 mx-auto px-4 text-white">
        <div className="h-fit-content">
          <div className="relative max-w-none xl:max-w-md">
            <div className="font-heading mb-5 text-4xl font-extrabold leading-none lg:leading-tight xl:text-5xl">
              <div>
                <span className="text-white">Geospatial analytics made easy</span>
              </div>
            </div>
            <p className="text-base lg:text-lg xl:text-xl text-white-200 mb-9 leading-snug">
              Draw and edit geofences and connect directly to your database
            </p>
            <EmailBox />
            <InvestorSection />
          </div>
        </div>
        <div className="relative hidden sm:block h-[90%]">
          <Globe />
        </div>
      </div>
    </section>
  );
};
