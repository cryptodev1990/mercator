import { ShapeEditor } from "./editor-tab/editor-tab";
import { useShapes } from "../../hooks/use-shapes";
import Loading from "react-loading";
import { ShapeBarPaginator } from "./shape-list-tab/shape-list-tab";
import { SidebarDrawer } from "./hideable-drawer";
import { GeofencerNavbar } from "../navbar";
import { Footer } from "./footer";

const SidebarNavigation = () => {
  const { shapeForPropertyEdit, setShapeForPropertyEdit } = useShapes();
  return (
    <nav className="flex" aria-label="Breadcrumb">
      <ol className="inline-flex items-center space-x-1 md:space-x-3">
        <li className="inline-flex items-center">
          <a
            href="#"
            className="inline-flex items-center text-sm font-medium text-gray-700 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white"
          >
            <button
              className="text-white rounded hover:text-red-400 bg-opacity-0 border-none capitalize text-sm"
              onClick={() => setShapeForPropertyEdit(null)}
            >
              {"Home"}
            </button>
          </a>
        </li>
        <li aria-current="page">
          <div className="flex items-center">
            <svg
              className="w-6 h-6 text-gray-400"
              fill="currentColor"
              viewBox="0 0 20 20"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                fill-rule="evenodd"
                d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
                clip-rule="evenodd"
              />
            </svg>
            <span className="ml-1 text-sm font-medium text-gray-500 md:ml-2 dark:text-gray-400">
              {shapeForPropertyEdit?.name}
            </span>
          </div>
        </li>
      </ol>
    </nav>
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
      <div className="relative">
        <header className="bg-slate-800 sticky top-0 z-50">
          <GeofencerNavbar />
        </header>
        {!shapeForPropertyEdit && <ShapeBarPaginator />}
        <div>
          {shapeForPropertyEdit && (
            <div className="float-left p-2">
              <div className="pl-3 pb-0 m-0">
                <SidebarNavigation />
              </div>
              <ShapeEditor />
            </div>
          )}
        </div>
      </div>
      <div className="sticky bottom-0 left-0 w-full z-50">
        {!shapeForPropertyEdit && <Footer />}
      </div>
    </SidebarDrawer>
  );
};
export { GeofencerSidebar };
