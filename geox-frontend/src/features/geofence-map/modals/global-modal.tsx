import { useUiModals } from "../hooks/use-ui-modals";
import { UIModalEnum } from "../types";
import { DbSyncModal } from "./db-sync-modal";
import { UploadModal } from "./upload-modal/index";

export const GlobalModal = () => {
  const { modal } = useUiModals();

  return (
    <div>
      {modal === UIModalEnum.UploadShapesModal && <UploadModal />}
      {modal === UIModalEnum.DbSyncModal && <DbSyncModal />}
    </div>
  );
};
