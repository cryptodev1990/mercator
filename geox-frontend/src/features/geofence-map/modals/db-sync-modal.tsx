import { BiLink } from "react-icons/bi";
import { useDbSync } from "../hooks/use-db-sync";
import { useUiModals } from "../hooks/use-ui-modals";
import { UIModalEnum } from "../types";
import { ModalCard } from "./modal-card";

export const DbSyncModal = () => {
  const { modal, closeModal } = useUiModals();
  const { triggerCopyTask } = useDbSync();

  return (
    <ModalCard
      open={modal === UIModalEnum.DbSyncModal}
      onClose={closeModal}
      onSubmit={() => {
        triggerCopyTask();
        closeModal();
      }}
      icon={<BiLink className="h-6 w-6 text-green-600" aria-hidden="true" />}
      title="Upload to your database"
    >
      <div>
        <p>
          Click to sync the shape data here to an S3 bucket, Snowflake database,
          or Redshift.
        </p>
      </div>
    </ModalCard>
  );
};
