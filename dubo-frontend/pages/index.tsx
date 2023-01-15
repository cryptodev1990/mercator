import Head from "next/head";
import DemoBox from "../lib/demo-box";
import Navbar from "../lib/navbar";
import Link from "next/link";
import InfoCard from "../lib/info-card";

export default function Home() {
  return (
    <>
      <Head>
        <title>dubo Analytics</title>
        <meta name="description" content="Analytics made easy" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <main>
        <div>
          <Navbar />
        </div>
        <div className="max-w-4xl m-auto">
          <section className="flex flex-col items-center justify-center w-full">
            <div className="p-10 flex flex-col mx-auto items-center gap-5 animate-fadeInSlow">
              <h1 className="text-8xl font-bold text-spBlue">dubo</h1>
              <div>
                <h2 className="text-2xl">
                  Analytics in English, powered by AI
                </h2>
                <p className="w-[200px]"></p>
              </div>
            </div>
            <div className="animate-fadeInSlow flex flex-col justify-center items-center h-[200px] overflow-hidden">
              <br />
              <DemoBox />
            </div>
          </section>
          <section className="grid grid-rows-3 max-w-xl mx-auto px-10">
            <InfoCard header={"Dev-friendly"}>
              <p>
                Get started in minutes for free with our Python SDK at{" "}
                <code className="text-spBlue whitespace-pre">
                  pip install dubo
                </code>{" "}
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
                We never see a single row of data without your consent, even in
                our free tier product. Your data content stays in your browser.
              </p>
            </InfoCard>
            <InfoCard header={"Query data anywhere"}>
              <p className="">
                Use our Slack bot, our Chrome extension, or our web interface,
                coming soon, and use our integrations with SaaS providers like
                Greehouse and Salesforce.
              </p>
            </InfoCard>
          </section>
          <section>
            <div className="flex flex-col items-center justify-center h-full">
              <br />
              <Link
                href="/demo"
                className="text-3xl font-bold text-spBlue underline cursor-pointer"
              >
                Try our interactive demo
              </Link>
              <br />
            </div>
          </section>
        </div>
      </main>
    </>
  );
}