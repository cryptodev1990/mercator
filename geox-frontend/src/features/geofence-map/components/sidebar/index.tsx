import { ShapeEditor } from "./editor-tab/editor-tab";
import { useShapes } from "../../hooks/use-shapes";
import Loading from "react-loading";
import { ShapeBarPaginator } from "./shape-list-tab/shape-list-tab";
import { SidebarDrawer } from "./hideable-drawer";
import { GeofencerNavbar } from "../navbar";
import { Footer } from "./footer";

const BackToPaginatorButton = () => {
  const { setShapeForPropertyEdit } = useShapes();
  return (
    <button
      className="text-white rounded hover:text-red-400 bg-opacity-0 border-none capitalize text-sm"
      onClick={() => setShapeForPropertyEdit(null)}
    >
      {"<< Back"}
    </button>
  );
};

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
      <header className="bg-slate-800">
        <GeofencerNavbar />
      </header>
      {!shapeForPropertyEdit && <ShapeBarPaginator />}
      <div>
        {shapeForPropertyEdit && (
          <div className="float-left p-2">
            <div className="pl-3 pb-0 m-0">
              <BackToPaginatorButton />
            </div>
            <ShapeEditor />
          </div>
        )}
      </div>
      <div className="absolute bottom-0 w-full">
        {!shapeForPropertyEdit && <Footer />}
      </div>
    </SidebarDrawer>
  );
};
export { GeofencerSidebar };
