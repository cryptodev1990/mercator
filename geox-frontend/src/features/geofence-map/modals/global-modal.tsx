import { useUiModals } from "../hooks/use-ui-modals";
import { UIModalEnum } from "../types";
import { DbSyncModal } from "./db-sync-modal";
import { UploadModal } from "./upload-modal/index";
import { ExportShapesModal } from "./export-shapes-modal";
import { SupportModal } from "./support-modal";

export const GlobalModal = () => {
  const { modal } = useUiModals();
  return (
    <div>
      {modal === UIModalEnum.UploadShapesModal && <UploadModal />}
      {modal === UIModalEnum.ExportShapesModal && <ExportShapesModal />}
      {modal === UIModalEnum.DbSyncModal && <DbSyncModal />}
      {modal === UIModalEnum.SupportModal && <SupportModal />}
    </div>
  );
};
