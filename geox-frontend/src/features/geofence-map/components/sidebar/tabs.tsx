import { ReactNode, useState } from "react";
import { Tab } from "@headlessui/react";
import { useEffect } from "react";
import { GeofencerNavbar } from "../navbar";
import { TbListDetails, TbNotebook } from "react-icons/tb";
import { useShapes } from "../../hooks/use-shapes";

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
  const { shapeForPropertyEdit, setShapeForPropertyEdit } = useShapes();

  useEffect(() => {
    setSelectedIndex(active);
  }, [active]);

  useEffect(() => {
    if (active !== selectedIndex) {
      setShapeForPropertyEdit(null);
    }
  }, [selectedIndex]);

  const activeColorCss = (selected: boolean) =>
    selected ? "stroke-white" : "stroke-gray-300";

  return (
    <div className="h-full">
      <Tab.Group selectedIndex={selectedIndex} onChange={setSelectedIndex}>
        <section className="flex flex-col h-full">
          <div>
            <header className="bg-slate-800 flex-1">
              <div className="flex flex-row justify-between items-baseline">
                <GeofencerNavbar />
              </div>
            </header>
            <Tab.List className="my-1 relative">
              {tabnames.map((tabname: string, index: number) => (
                <Tab
                  key={index}
                  disabled={index === 1 && !shapeForPropertyEdit}
                  className={
                    "transition px-2 hover:text-porsche selection:bg-porsche mx-2"
                  }
                >
                  {index === 0 && (
                    <TbListDetails
                      className={activeColorCss(index === selectedIndex)}
                      data-tip={"Layers list"}
                    />
                  )}
                  {index === 1 && (
                    <TbNotebook
                      className={activeColorCss(index === selectedIndex)}
                      data-tip={"Property editor - select a shape to edit"}
                    />
                  )}
                  {index === selectedIndex && (
                    <div className="mt-1 h-0.5 w-5 bg-white absolute" />
                  )}
                </Tab>
              ))}
            </Tab.List>
          </div>
          <Tab.Panels>
            {children.map((child: any, index: number) => (
              <Tab.Panel key={index}>{child}</Tab.Panel>
            ))}
          </Tab.Panels>
        </section>
      </Tab.Group>
    </div>
  );
}
