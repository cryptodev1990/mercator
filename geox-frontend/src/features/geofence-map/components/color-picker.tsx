"use strict";

import React from "react";
import reactCSS from "reactcss";
import { SketchPicker, RGBColor } from "react-color";
import { Namespace, NamespacesService } from "client";
import { useMutation, useQueryClient } from "react-query";
import toast from "react-hot-toast";
import { useShapes } from "../hooks/use-shapes";

export function SketchExampleHook({ namespace }: { namespace: Namespace }) {
  const [displayColorPicker, setDisplayColorPicker] = React.useState(false);

  const [color, setColor] = React.useState<RGBColor>(
    namespace.properties.color
  );

  const handleClick = () => {
    setDisplayColorPicker(!displayColorPicker);
  };

  const handleClose = () => {
    setDisplayColorPicker(false);
  };

  const qc = useQueryClient();

  const { tileUpdateCount, setTileUpdateCount } = useShapes();

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
              ? { ...prevNamespace, properties: newNamespace.properties }
              : prevNamespace
          )
        );
      }
      setTileUpdateCount(tileUpdateCount + 1);
    },
    onError: (error: any) => {
      if (error.message) toast.error(error.message);
      else toast.error("Error occured updating namespace");
    },
  });

  const styles = reactCSS({
    default: {
      color: {
        width: 8,
        height: 8,
        background: `rgba(${color.r}, ${color.g}, ${color.b}, ${color.a})`,
      },
      swatch: {
        padding: 1,
        background: "#fff",
        borderRadius: "1px",
        boxShadow: "0 0 0 1px rgba(0,0,0,.1)",
        display: "inline-block",
        cursor: "pointer",
      },
      popover: {
        position: "absolute",
        zIndex: 2,
      },
      cover: {
        position: "fixed",
        top: "0px",
        right: "0px",
        bottom: "0px",
        left: "0px",
      },
    },
  });

  return (
    <div>
      <div style={styles.swatch} onClick={handleClick}>
        <div style={styles.color} />
      </div>
      {displayColorPicker ? (
        <div
          style={{
            position: "absolute",
            zIndex: "100",
          }}
        >
          <div
            style={{
              position: "fixed",
              top: "0px",
              right: "0px",
              bottom: "0px",
              left: "0px",
            }}
            onClick={handleClose}
          />
          <SketchPicker
            color={color}
            onChange={(d) => setColor(d.rgb)}
            onChangeComplete={(d) => {
              mutation.mutate({
                id: namespace.id,
                properties: { color: d.rgb },
              });
            }}
          />
        </div>
      ) : null}
    </div>
  );
}
