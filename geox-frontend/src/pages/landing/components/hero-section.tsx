import { EmailBox } from "./email-box";
import logo from "../../../common/assets/mercator-logo.svg";

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
          key={investor.name}
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
  return (
    <section className="m-10 relative">
      <div className="max-w-full sm:max-w-[50%] text-white flex flex-col justify-start">
        <a href="/">
          <img src={logo} alt="logo" className="h-12" />
        </a>
        <span className="text-white font-normal text-3xl">
          Geospatial analytics made easy
        </span>
        <p className="mt-5">
          Mercator provides a suite of tools for manipulating data in space.
          We're starting with{" "}
          <a className="font-bold hover:underline" href="#geofencer-features">
            Geofencer
          </a>
          , our tool for annotating and creating map data.{" "}
          <a className="font-bold hover:underline" href="/subscribe">
            Try it for free.
          </a>
        </p>
        <div className="py-10">
          <EmailBox autoFocus />
        </div>
        <div>
          <InvestorSection />
        </div>
      </div>
    </section>
  );
};
