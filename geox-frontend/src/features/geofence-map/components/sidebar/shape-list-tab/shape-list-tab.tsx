import { useShapes } from "../../../hooks/use-shapes";
import {
  AddToQueueIcon,
  JsonIcon,
  FillDatabaseIcon,
} from "../../../../../common/components/icons";
import Loading from "react-loading";
import { useUiModals } from "../../../hooks/use-ui-modals";
import { UIModalEnum } from "../../../types";
import { useDbSync } from "../../../hooks/use-db-sync";
import { NamespaceSection } from "./namespace-section";
import { TentativeButtonBank } from "./shape-card/button-bank";

export const ShapeBarPaginator = () => {
  const { tentativeShapes, numShapes, namespaces } = useShapes();
  const { openModal } = useUiModals();
  const { isLoading: isPolling } = useDbSync();

  const topBarButtons = [
    {
      icon: <AddToQueueIcon className="fill-white" />,
      disabled: false,
      onClick: () => openModal(UIModalEnum.UploadShapesModal),
      text: "Upload",
      dataTip: "Upload a GeoJSON or other shape file",
    },
    {
      icon: <JsonIcon className="fill-white" size={15} />,
      disabled: numShapes === 0,
      dataTip: "Export shapes as GeoJSON",
      onClick: () => openModal(UIModalEnum.ExportShapesModal),
      text: "Export",
    },
    {
      icon: isPolling ? (
        <Loading className="spin" height={20} width={20} />
      ) : (
        <FillDatabaseIcon className="fill-white" />
      ),
      dataTip: "Publish shapes to your Snowflake or Redshift database",
      disabled: isPolling || numShapes === 0,
      onClick: () => {
        if (isPolling) return;
        openModal(UIModalEnum.DbSyncModal);
      },
      text: "DB Sync",
    },
  ];

  return (
    <div id="shape-list" className="flex flex-col flex-1">
      <div className="bg-slate-700 flex flex-row justify-between cursor-pointer">
        {topBarButtons.map((button, i) => (
          <button
            key={i}
            disabled={button.disabled}
            className="btn btn-xs h-10 rounded-none bg-slate-700 text-white space-x-1 grow"
            onClick={button.onClick}
            data-tip={button.dataTip}
            data-tip-skew="right"
          >
            {button.icon}{" "}
            <label className="cursor-pointer">{button.text}</label>
          </button>
        ))}
      </div>
      {tentativeShapes.length > 0 && <TentativeButtonBank />}
      {namespaces.length !== 0 && (
        <NamespaceSection
          className="
          flex-1
          h-full p-1 bg-gradient-to-b from-slate-600 to-slate-700
      "
        />
      )}
    </div>
  );
};
