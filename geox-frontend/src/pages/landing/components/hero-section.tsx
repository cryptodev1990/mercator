import { EmailBox } from "./email-box";
import logo from "../../../common/assets/mercator-logo.svg";
// import logoYc from "../images/yc-logo.png";
// import logoTribeCapital from "../images/Tribe_Capital_logo.webp";
// import logoSoma from "../images/Soma_Capital_logo.webp";
// import logoRebel from "../images/Rebel_Fund_logo.webp";
// import logoAmplify from "../images/Amplify_Partners_logo.jpeg";
// import logoValor from "../images/Valor_Equity_Partners_logo.webp";

import { useEffect, useRef } from "react";

function Investor(url: string, logo: string | null, name: string): InvestorT {
  return {
    url,
    logo,
    name,
  };
}

type InvestorT = {
  url: string;
  logo: string | null;
  name: string;
};

export const InvestorSection = (): JSX.Element => {
  const investors = [
    Investor("https://www.ycombinator.com/", null, "Y Combinator"),
    Investor("https://tribecap.co/", null, "Tribe Capital"),
    Investor("https://www.rebelfund.vc/", null, "Rebel Fund"),
    Investor("https://www.somacap.com/", null, "Soma Capital"),
    Investor("https://www.valorep.com/", null, "Valor Equity Partners"),
    Investor("https://amplifypartners.com/", null, "Amplify Partners"),
  ];

  return (
    <div>
      <span className="font-bold font-serif text-purple-200 text-left">
        Backed by
      </span>
      {investors.map((investor: InvestorT, i: number) => (
        <a
          href={investor.url}
          target="_blank"
          rel="noreferrer"
          className="first-of-type:pl-4 select-none cursor-pointer"
          style={{}}
        >
          {!investor.logo && (
            <span className="text-slate-100 font-serif inline-block leading-4">
              {investor.name}
            </span>
          )}
          {i !== investors.length - 1 && (
            <span className="text-purple-200 font-serif inline-block leading-4">
              &nbsp;&bull;&nbsp;
            </span>
          )}
        </a>
      ))}
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
    <section ref={ref} className="m-10 relative">
      <div className="max-w-full sm:max-w-[50%] text-white flex flex-col justify-start">
        <a href="/">
          <img src={logo} alt="logo" className="h-12" />
        </a>
        <span className="text-white font-normal text-3xl">
          Geospatial analytics made easy
        </span>
        <div className="py-10">
          <EmailBox />
        </div>
        <div>
          <InvestorSection />
        </div>
      </div>
    </section>
  );
};
