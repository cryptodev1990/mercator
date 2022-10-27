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
  }, [selectedIndex, active, setShapeForPropertyEdit]);

  const activeColorCss = (selected: boolean) =>
    selected ? "stroke-white" : "stroke-gray-300";

  return (
    <div className="h-full flex flex-col">
      <Tab.Group selectedIndex={selectedIndex} onChange={setSelectedIndex}>
        <section className="h-full flex flex-col">
          <header className="bg-slate-800">
            <GeofencerNavbar />
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
                  />
                )}
                {index === selectedIndex && (
                  <div className="mt-1 h-0.5 w-5 bg-white absolute" />
                )}
              </Tab>
            ))}
          </Tab.List>
          <Tab.Panels className="flex-auto">
            {children.map((child: any, index: number) => (
              <Tab.Panel className="h-full" key={index}>
                {child}
              </Tab.Panel>
            ))}
          </Tab.Panels>
        </section>
      </Tab.Group>
    </div>
  );
}
