import { Tabs } from "./tabs";
import { ShapeEditor } from "./editor-tab/editor-tab";
import { useShapes } from "../../hooks/use-shapes";
import Loading from "react-loading";
import { ShapeBarPaginator } from "./shape-list-tab/shape-list-tab";
import { SidebarDrawer } from "./hideable-drawer";

const GeofencerSidebar = () => {
  const { shapeForPropertyEdit, shapeMetadataIsLoading } = useShapes();

  if (shapeMetadataIsLoading) {
    return (
      <SidebarDrawer>
        <div className="w-max m-auto">
          <Loading type="bubbles" />
        </div>
      </SidebarDrawer>
    );
  }

  return (
    <SidebarDrawer>
      <Tabs
        children={[<ShapeBarPaginator />, <ShapeEditor />].map((x, i) => (
          <div className="h-full" key={i}>
            {x}
          </div>
        ))}
        active={!shapeForPropertyEdit ? 0 : 1}
        tabnames={["Shapes", "Metadata Editor"]}
      />
    </SidebarDrawer>
  );
};
export { GeofencerSidebar };
