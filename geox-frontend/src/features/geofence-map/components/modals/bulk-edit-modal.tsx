import { useUiModals } from "features/geofence-map/hooks/use-ui-modals";
import { UIModalEnum } from "features/geofence-map/types";
import { ModalCard } from "./modal-card";

const BulkEditModal = () => {
  const { modal, closeModal } = useUiModals();

  return (
    <ModalCard
      open={modal === UIModalEnum.BulkEditModal}
      onClose={closeModal}
      icon={"Icon"}
      title="Report a bug or request a feature"
    >
      <div>
        <p className="text-slate-600">This is a bulk edit modal</p>
      </div>
    </ModalCard>
  );
};

export default BulkEditModal;
