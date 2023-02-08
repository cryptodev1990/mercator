import { useContext, useEffect, useState } from "react";
import {
  EyeFillIcon,
  EyeSlashFillIcon,
  CaretRightIcon,
} from "../../../../../../common/components/icons";
import { Namespace, NamespacesService } from "../../../../../../client";
import { EditableLabel } from "../../../../../../common/components/editable-label";
import { useShapes } from "../../../../hooks/use-shapes";
import { DragTarget } from "../shape-card/drag-handle";
import { ShapeCard } from "../shape-card/shape-card";
import { DeleteButton } from "./delete-button";
import simplur from "simplur";
import { useSelectedShapes } from "../../../../hooks/use-selected-shapes";
import { SearchContext } from "../../../../contexts/search-context";
import { MAX_DISPLAY_SHAPES, Paginator } from "./paginator";
import {
  useGetNamespaces,
  usePatchShapeMutation,
} from "features/geofence-map/hooks/use-openapi-hooks";
import { useMutation, useQueryClient } from "react-query";
import toast from "react-hot-toast";
import ReactLoading from "react-loading";
import { ColorPicker } from "features/geofence-map/components/color-picker";

export const NamespaceCard = ({
  namespace,
  onClickCaret,
  isVisible,
  shouldOpen,
}: {
  namespace: Namespace;
  onClickCaret: () => void;
  shouldOpen: boolean;
  isVisible: boolean;
}) => {
  const { visibleNamespaces, setVisibleNamespaces } = useShapes();
  const { dispatch: selectionDispatch } = useSelectedShapes();

  const { mutate: patchShapeById } = usePatchShapeMutation();

  const qc = useQueryClient();

  const mutation = useMutation(NamespacesService.patchNamespace, {
    onSuccess: async (newNamespace) => {
      await qc.cancelQueries(["geofencer"]);
      const previousNamespaces: Namespace[] | undefined = qc.getQueryData([
        "geofencer",
      ]);
      if (previousNamespaces) {
        qc.setQueryData(
          ["geofencer"],
          previousNamespaces.map((prevNamespace: Namespace) =>
            prevNamespace.id === newNamespace.id
              ? { ...newNamespace, shapes: prevNamespace.shapes }
              : prevNamespace
          )
        );
      }
    },
    onError: (error: any) => {
      if (error.message) toast.error(error.message);
      else toast.error("Error occured updating namespace");
    },
  });

  const { data: allNamespaces } = useGetNamespaces();

  const [hovered, setHovered] = useState(false);
  const { searchResults } = useContext(SearchContext);
  // support pages
  const [page, setPage] = useState(0);
  const [maxPage, setMaxPage] = useState(0);

  useEffect(() => {
    if (allNamespaces) {
      const sectionShapeMetadata = allNamespaces
        ?.flatMap((x) => x.shapes ?? [])
        .filter((shape) => shape.namespace_id === namespace.id);

      setMaxPage(Math.ceil(sectionShapeMetadata.length / MAX_DISPLAY_SHAPES));
    }
  }, [namespace.shapes]);

  const sectionShapeMetadata = allNamespaces
    ?.flatMap((x) => x.shapes ?? [])
    .filter((shape) => shape.namespace_id === namespace.id);

  return (
    <DragTarget
      id={`namespace-card-${namespace.slug}`}
      className={`snap-start bg-slate-600 border-gray-200`}
      handleDragOver={(e: React.DragEvent) => {
        const data = e.dataTransfer.getData("text");
        patchShapeById({ uuid: data, namespace: namespace.id });
      }}
    >
      {/* Namespace header */}
      <div
        className="flex items-center cursor-pointer px-3"
        onMouseEnter={() => setHovered(true)}
        onMouseLeave={() => setHovered(false)}
      >
        <button
          onClick={onClickCaret}
          className={`transition ${shouldOpen ? "rotate-90" : ""}`}
        >
          <CaretRightIcon />
        </button>
        <div>
          <ColorPicker namespace={namespace} />
        </div>
        <div
          {...(namespace.name.length > 20
            ? { "data-tip": namespace.name, "data-tip-skew": "right" }
            : {})}
          data-tip-skew="right"
        >
          <EditableLabel
            className="font-bold text-md mx-1 select-none text-white w-48"
            value={namespace.name}
            onChange={(newName) => {
              if (newName !== namespace.name) {
                mutation.mutate({
                  id: namespace.id,
                  name: newName,
                });
              }
            }}
            disabled={namespace.is_default}
          />
        </div>
        {mutation.isLoading ? (
          <ReactLoading type="spin" height={"15px"} width={"15px"} />
        ) : null}
        <div className="self-center ml-auto z-10 flex space-x-3">
          {/* {sectionShapeMetadata && hovered && (
            <span className="text-sm">{simplur`${sectionShapeMetadata.length} shape[|s]`}</span>
          )} */}
          {!namespace.is_default && hovered && (
            <DeleteButton namespace={namespace} />
          )}
          <div
            onClick={() => {
              selectionDispatch({ type: "RESET_SELECTION" });
              if (isVisible) {
                setVisibleNamespaces(
                  visibleNamespaces.filter((x) => x.id !== namespace.id)
                );
              } else {
                setVisibleNamespaces([...visibleNamespaces, namespace]);
              }
            }}
          >
            <span data-tip="Click to show/hide layer" data-tip-skew="right">
              {isVisible ? <EyeFillIcon /> : <EyeSlashFillIcon />}
            </span>
          </div>
        </div>
      </div>
      <hr />
      {/* Directory body */}
      {shouldOpen && (
        <div>
          {sectionShapeMetadata &&
            sectionShapeMetadata.length > 0 &&
            sectionShapeMetadata
              .filter((x, i) => {
                if (searchResults && searchResults.size > 0) {
                  return searchResults.has(x.uuid);
                } else {
                  return (
                    i >= page * MAX_DISPLAY_SHAPES &&
                    i < (page + 1) * MAX_DISPLAY_SHAPES
                  );
                }
              })
              .map((x, i) => <ShapeCard shape={x} key={x.uuid} />)}
          {(!searchResults || searchResults.size === 0) &&
            sectionShapeMetadata &&
            sectionShapeMetadata.length > MAX_DISPLAY_SHAPES && (
              <Paginator
                maxShapes={sectionShapeMetadata.length}
                page={page}
                setPage={setPage}
                maxPage={maxPage}
              />
            )}
        </div>
      )}
    </DragTarget>
  );
};
