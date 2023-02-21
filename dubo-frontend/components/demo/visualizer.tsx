import * as fluentui from "@fluentui/react";
import * as vega from "vega";
import * as React from "react";
import * as ReactDOM from "react-dom";
import "@msrvida/sanddance-explorer/dist/css/sanddance-explorer.css";

const Visualizer = ({ header, data }: { header: any[]; data: any[] }) => {
  const [SandDance, setSandDance] = React.useState();

  const explorerProps = {
    logoClickUrl: "https://microsoft.github.io/SandDance/",
    mounted: (explorer: any) => {
      explorer.load(
        data.map((d) =>
          header.reduce((acc, h, index) => ({ ...acc, [h]: d[index] }), {})
        )
      );
    },
  };

  React.useEffect(() => {
    if (window && window.innerWidth > 550) {
      fluentui.initializeIcons();

      const use = async () => {
        const sd = await import("@msrvida/sanddance-explorer");
        sd.use(fluentui, React, ReactDOM, vega);
        setSandDance(sd as any);
      };
      use();
    }
  }, []);

  if (!SandDance) return null;

  return (
    <>
      <div className="mt-4 animate-fadeIn-100">
        {/* @ts-ignore */}
        <SandDance.Explorer {...explorerProps} />
      </div>
    </>
  );
};

export default Visualizer;
