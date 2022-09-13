import { useContext } from "react";
import { UIContext } from "../contexts/ui-context";
import { UIModalEnum } from "../types";

export const useUiModals = () => {
  const { modal, setModal } = useContext(UIContext);

  function openModal(modalName: string) {
    const modalValues = Object.values(UIModalEnum).includes(
      modalName as UIModalEnum
    );
    if (modalValues) {
      setModal(modalName as UIModalEnum);
    } else {
      throw new Error(`Modal ${modalName} does not exist`);
    }
  }

  function closeModal() {
    setModal(null);
  }

  return { modal, openModal, closeModal };
};
