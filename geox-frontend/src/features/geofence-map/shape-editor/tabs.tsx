import { useState } from "react";
import { Tab } from "@headlessui/react";
import { useEffect } from "react";
import { useEditableShape } from "./hooks";

export function Tabs({
  children,
  tabnames,
  active,
}: {
  children: any;
  tabnames: string[];
  active: number;
}) {
  const [selectedIndex, setSelectedIndex] = useState(0);
  const { setShapeForEdit } = useEditableShape();

  useEffect(() => {
    setSelectedIndex(active);
  }, [active]);

  useEffect(() => {
    if (active !== selectedIndex) {
      setShapeForEdit(null);
    }
  }, [selectedIndex]);

  return (
    <Tab.Group selectedIndex={selectedIndex} onChange={setSelectedIndex}>
      <Tab.List>
        {tabnames.map((tabname: string, index: number) => (
          <Tab
            key={index}
            className={
              "transition px-2 hover:text-porsche" +
              (selectedIndex === index
                ? " bg-slate-900 translate-y-[-3px] p-1"
                : "bg-white")
            }
          >
            {tabname}
          </Tab>
        ))}
      </Tab.List>
      <Tab.Panels>
        {children.map((child: any, index: number) => (
          <Tab.Panel key={index}>{child}</Tab.Panel>
        ))}
      </Tab.Panels>
    </Tab.Group>
  );
}
