import { useState } from "react";
import { Tab } from "@headlessui/react";
import { useMetadataEditModal } from "../../features/geofence-map/metadata-editor/hooks";
import { useEffect } from "react";

export function Tabs({
  children,
  tabnames,
}: {
  children: any;
  tabnames: string[];
}) {
  const [selectedIndex, setSelectedIndex] = useState(0);
  const { shapeForEdit } = useMetadataEditModal();

  useEffect(() => {
    if (shapeForEdit) {
      setSelectedIndex(1);
    } else {
      setSelectedIndex(0);
    }
    return () => {};
  }, [shapeForEdit]);

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
