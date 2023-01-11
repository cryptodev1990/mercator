import Head from "next/head";
import DemoBox from "./demo-box";
import Navbar from "./navbar";
import DiscordBar from "./discord-bar";

const Section = ({
  children,
  size,
}: {
  children: React.ReactNode;
  size: string;
}) => {
  return (
    <div
      className={`flex flex-col items-center justify-center w-full h-${size}`}
    >
      {children}
    </div>
  );
};

const Navitem = ({ children }: { children: React.ReactNode }) => {
  return (
    <div className="flex flex-row items-center justify-center w-1/3 h-full space-x-3">
      {children}
    </div>
  );
};

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
          <Navbar>
            <Navitem>
              <div className="text-2xl font-bold ">dubo</div>
            </Navitem>
            <Navitem>
              <div className="text-lg ">Pricing</div>
              <div className="text-lg ">About</div>
            </Navitem>
          </Navbar>
          <DiscordBar />
        </div>
        <Section size="3/4">
          <div className="p-10 flex flex-row mx-auto items-center gap-5 animate-fadeInSlow">
            <h1 className="text-8xl font-bold text-spBlue">dubo</h1>
            <h2 className="text-2xl">Analytics made easy</h2>
          </div>
          <div className="animate-fadeInSlow flex flex-col justify-center items-center">
            <DemoBox />
          </div>
        </Section>
      </main>
    </>
  );
}
