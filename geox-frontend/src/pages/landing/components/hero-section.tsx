import { EmailBox } from "./email-box";
import logoYc from "../images/yc-logo.png";
import logoTribeCapital from "../images/Tribe_Capital_logo.webp";
import logoSoma from "../images/Soma_Capital_logo.webp";
import logoRebel from "../images/Rebel_Fund_logo.webp";
import logoAmplify from "../images/Amplify_Partners_logo.jpeg";
import logoValor from "../images/Valor_Equity_Partners_logo.webp";

import { Globe } from "./globe";
import { useEffect, useRef } from "react";

export const InvestorSection = (): JSX.Element => {
  const investors = [
    [
      {
        url: "https://www.ycombinator.com/",
        logo: logoYc,
        name: "Y Combinator",
      },
      {
        url: "https://tribecap.co/",
        logo: logoTribeCapital,
        name: "Tribe Capital",
      },
      {
        url: "https://www.rebelfund.vc/",
        logo: logoRebel,
        name: "Rebel Fund",
      },
    ],
    [
      {
        url: "https://www.somacap.com/",
        logo: logoSoma,
        name: "Soma Capital",
      },
      {
        url: "https://www.valorep.com/",
        logo: logoValor,
        name: "Valor Equity Partners",
      },
      {
        url: "https://amplifypartners.com/",
        logo: logoAmplify,
        name: "Amplify Partners",
      },
    ],
  ];

  return (
    <div className="mt-5 py5 text-xs font-bold">
      <p className="font-display text-base text-white">Backed by</p>
      <ul className="py-2 flex items-left justify-left gap-x-5 sm:flex-col sm:gap-x-0 sm:gap-y-2 xl:flex-row xl:gap-x-5 xl:gap-y-0">
        {investors.map((group, groupIndex) => (
          <li key={groupIndex}>
            <ul className="flex flex-col items-left gap-y-2 sm:flex-row sm:gap-x-5 sm:gap-y-0">
              {group.map((investor) => (
                <li key={investor.name} className="flex">
                  <div>
                    <a
                      href={investor.url}
                      target="_blank"
                      rel="noreferrer"
                      className="select-none cursor-default"
                      style={{
                        display: "inline-block",
                        height: "60px",
                        width: "auto",
                      }}
                    >
                      <img
                        src={investor.logo}
                        alt={investor.name}
                        className="h-[60px] w-auto cursor-pointer"
                      ></img>
                    </a>
                  </div>
                </li>
              ))}
            </ul>
          </li>
        ))}
      </ul>
    </div>
  );
};

export const HeroSection = (): JSX.Element => {
  const ref = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (ref.current) {
      ref.current.focus();
    }
  }, [ref]);

  return (
    <section ref={ref} className="m-1">
      <div className="grid max-w-5xl md:grid-cols-2 gap-20 mx-auto px-4 text-white">
        <div className="h-fit-content">
          <div className="relative max-w-none xl:max-w-md">
            <div className="font-heading mb-5 text-4xl font-extrabold leading-none lg:leading-tight xl:text-5xl">
              <div>
                <span className="text-white">
                  Geospatial analytics made easy
                </span>
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
