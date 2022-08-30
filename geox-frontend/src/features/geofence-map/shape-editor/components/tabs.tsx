import { ReactNode, useState } from "react";
import { Tab } from "@headlessui/react";
import { useEffect } from "react";
import { GeofencerNavbar } from "../../geofencer-navbar";
import { TbListDetails, TbNotebook } from "react-icons/tb";
import { useShapes } from "../../hooks/use-shapes";
import { useTooltip } from "../../../../hooks/use-tooltip";
import ReactTooltip from "react-tooltip";

export function Tabs({
  children,
  tabnames,
  active,
}: {
  children: ReactNode[];
  tabnames: string[];
  active: number;
}) {
  const [selectedIndex, setSelectedIndex] = useState(0);
  const { shapeForMetadataEdit, setShapeForMetadataEdit } = useShapes();

  useEffect(() => {
    setSelectedIndex(active);
  }, [active]);

  useEffect(() => {
    if (active !== selectedIndex) {
      setShapeForMetadataEdit(null);
    }
  }, [selectedIndex]);

  const { tooltip, tooltipEvents } = useTooltip();

  const activeColorCss = (selected: boolean) =>
    selected ? "stroke-white" : "stroke-gray-300";

  return (
    <>
      <Tab.Group selectedIndex={selectedIndex} onChange={setSelectedIndex}>
        <section className="flex flex-col">
          <header className="bg-slate-800 flex-1">
            <div className="flex flex-row justify-between items-baseline">
              <GeofencerNavbar />
            </div>
            <Tab.List className="my-1 relative">
              {tabnames.map((tabname: string, index: number) => (
                <Tab
                  key={index}
                  disabled={index === 1 && !shapeForMetadataEdit}
                  className={
                    "transition px-2 hover:text-porsche selection:bg-porsche mx-2"
                  }
                >
                  {index === 0 && (
                    <TbListDetails
                      className={activeColorCss(index === selectedIndex)}
                      data-tip={"Layers list"}
                      {...tooltipEvents}
                    />
                  )}
                  {index === 1 && (
                    <TbNotebook
                      className={activeColorCss(index === selectedIndex)}
                      data-tip={"Property editor - select a shape to edit"}
                      {...tooltipEvents}
                    />
                  )}
                  {index === selectedIndex && (
                    <div className="mt-1 h-0.5 w-5 bg-white absolute" />
                  )}
                </Tab>
              ))}
            </Tab.List>
          </header>
          <Tab.Panels className="relative flex-auto bg-slate-700">
            {children.map((child: any, index: number) => (
              <Tab.Panel key={index}>{child}</Tab.Panel>
            ))}
          </Tab.Panels>
          {tooltip && <ReactTooltip effect="solid" place="left" type="dark" />}
        </section>
      </Tab.Group>
    </>
  );
}
