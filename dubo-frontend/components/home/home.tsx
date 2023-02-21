import Link from "next/link";

import DemoBox from "./demo-box";
import InfoCard from "./info-card";
import EmailBox from "./email-box";

const Home = () => (
  <main className="flex flex-row justify-center w-full items-stretch">
    <div className="flex flex-col items-center justify-center max-w-lg">
      <div className="mb-10 flex flex-col mx-auto items-center gap-5 animate-fadeIn500">
        <h1 className="text-8xl font-bold text-spBlue">dubo</h1>
        <h2 className="text-2xl">Analytics in English, powered by AI</h2>
      </div>
      <div className="animate-fadeIn500 flex flex-col justify-center items-center h-[300px] sm:h-[220px] overflow-hidden w-full">
        <br />
        <DemoBox />
      </div>
      <br />
      <div className="flex flex-col items-center justify-center mt-3">
        <Link href="/demo">
          <button
            type="button"
            className="inline-block px-6 py-2.5 bg-spBlue text-white font-medium text-lg leading-tight shadow-md hover:bg-spBlueDark hover:shadow-lg focus:bg-spBlueDark focus:shadow-lg focus:outline-none focus:ring-0 active:shadow-lg transition duration-150 ease-in-out"
          >
            Try the demo
          </button>
        </Link>
      </div>
      <br />
      <div className="w-full flex flex-col items-center">
        <h4 className="text-2xl font-bold text-spBlue">
          Follow along for updates
        </h4>
        <EmailBox />
      </div>
      <InfoCard header={"Dev-friendly"}>
        <p>
          Get started in minutes for free with our Python SDK at{" "}
          <code className="text-spBlue whitespace-pre">pip install dubo</code>{" "}
          and check out{" "}
          <Link
            className="text-spBlue underline"
            href="https://mercatorhq.github.io/dubo-jl/retro/notebooks/?path=dubo.ipynb"
          >
            our demo Jupyter notebook
          </Link>
          .
        </p>
      </InfoCard>
      <InfoCard header={"Private by design"}>
        <p>
          We never see a single row of data without your consent, even in our
          free tier product. Your data content stays in your browser.
        </p>
      </InfoCard>
      <InfoCard header={"Query data anywhere"}>
        <p className="">
          Use our Slack bot, our Chrome extension, or our web interface, coming
          soon, and use our integrations with SaaS providers like Greenhouse and
          Salesforce.
        </p>
      </InfoCard>
    </div>
  </main>
);

export default Home;
