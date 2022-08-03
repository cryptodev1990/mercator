import { ReactNode, useState } from "react";
import { Tab } from "@headlessui/react";
import { useEffect } from "react";
import { GeofencerNavbar } from "../../geofencer-navbar";
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
  const { setShapeForMetadataEdit } = useShapes();

  useEffect(() => {
    setSelectedIndex(active);
  }, [active]);

  useEffect(() => {
    if (active !== selectedIndex) {
      setShapeForMetadataEdit(null);
    }
  }, [selectedIndex]);

  return (
    <>
      <Tab.Group selectedIndex={selectedIndex} onChange={setSelectedIndex}>
        <section className="flex flex-col">
          <header className="bg-slate-800 flex-1">
            <GeofencerNavbar />
            <Tab.List className="my-1 relative">
              {tabnames.map((tabname: string, index: number) => (
                <Tab
                  key={index}
                  className={
                    "transition px-2 hover:text-porsche selection:bg-porsche mx-2"
                  }
                >
                  {index === 0 && (
                    <TbListDetails
                      className={
                        index === selectedIndex
                          ? "stroke-white"
                          : "stroke-gray-300"
                      }
                    />
                  )}
                  {index === 1 && (
                    <TbNotebook
                      className={
                        index === selectedIndex
                          ? "stroke-white"
                          : "stroke-gray-300"
                      }
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
        </section>
      </Tab.Group>
    </>
  );
}