import { Tabs } from "./tabs";
import { ShapeEditor } from "./shape-editor";
import { useShapes } from "../../hooks/use-shapes";
import Loading from "react-loading";
import { ShapeBarPaginator } from "./ShapeBarPaginator";
import { SidebarDrawer } from "./sidebar-drawer";

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
          <div key={i}>{x}</div>
        ))}
        active={!shapeForPropertyEdit ? 0 : 1}
        tabnames={["Shapes", "Metadata Editor"]}
      />
    </SidebarDrawer>
  );
};
export { GeofencerSidebar };
