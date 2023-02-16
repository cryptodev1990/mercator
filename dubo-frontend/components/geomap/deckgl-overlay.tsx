import type { MapboxOverlayProps } from "@deck.gl/mapbox/typed";
import { MapboxOverlay } from "@deck.gl/mapbox/typed";
import { Map } from "mapbox-gl";
import { useEffect, useRef } from "react";

export function DeckGLOverlay(
  props: MapboxOverlayProps & {
    interleaved?: boolean;
    mapboxRef: React.MutableRefObject<Map>;
  }
) {
  // This could probably be a hook but it looks more natural as a React component
  const overlayRef = useRef<any>(null);

  useEffect(() => {
    // create the overlay
    const overlay = new MapboxOverlay({
      ...props,
    });
    // store it in a ref for later
    overlayRef.current = overlay;
    // connect it to the map
    props.mapboxRef.current.addControl(overlayRef.current);
    // clean up when the component unmounts
    return () => {
      if (window.location.pathname === "/demos/census/data-catalog") {
        props.mapboxRef.current.removeControl(overlayRef.current);
        // TODO why is the unmount not working?
      }
    };
  }, []);

  useEffect(() => {
    if (overlayRef?.current !== null && props) {
      // update the overlay anytime the props change
      overlayRef?.current?.setProps(props);
    }
    // clean up when the component unmounts
  }, [props]);

  // return null so that react doesn't try to render anything
  return null;
}
