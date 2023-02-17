import { useEffect, useState, useCallback } from "react";

import { base64ToString, stringToBase64 } from "../../utils";

type UrlState = {
  userQuery: string | null;
  lat: number | null;
  lng: number | null;
  zoom: number | null;
};

type UrlStateUpdate = {
  userQuery?: string | null;
  lat?: number | null;
  lng?: number | null;
  zoom?: number | null;
};

export function urlToUrlState(url: string) {
  const postHash = url.split("#")[1];
  if (!postHash) {
    return {
      userQuery: null,
      lat: null,
      lng: null,
      zoom: null,
    };
  }
  const realString = base64ToString(postHash);
  // The string should be split on the '||' character
  const splitString = realString.split("||");
  // The first half of the string is the user query
  const userQuery = splitString[0];
  // The second half of the string is the viewport state, a comma-separated list of lng,lat,zoom
  const [lng, lat, zoom] = splitString[1].split(",");
  return {
    userQuery,
    lat: parseFloat(lat),
    lng: parseFloat(lng),
    zoom: parseFloat(zoom),
  };
}

export function urlStateToUrl(urlState: UrlState) {
  const { userQuery, lat, lng, zoom } = urlState;
  const viewportState = `${lng},${lat},${zoom}`;
  const realString = `${userQuery}||${viewportState}`;
  const encodedString = stringToBase64(realString);
  return encodedString;
}

let _urlState = {
  userQuery: null,
  lat: null,
  lng: null,
  zoom: null,
} as UrlState;

// read the url state
export function useUrlState() {
  const [error, setError] = useState<Error | null>(null);
  const [copySuccess, setCopySuccess] = useState(false);
  const updateUrlState = (stateToMerge: UrlStateUpdate) => {
    _urlState = {
      ..._urlState,
      ...stateToMerge,
    };
  };

  useEffect(() => {
    // after 2 seconds, reset the copy success state
    if (!copySuccess) return;
    const timeout = setTimeout(() => {
      setCopySuccess(false);
    }, 1000);
    return () => clearTimeout(timeout);
  }, [copySuccess]);

  function copyShareUrl() {
    const newUrlHash = urlStateToUrl(_urlState);
    const currentUrl = window.location.href;
    // remove the hash from the current url
    const currentUrlWithoutHash = currentUrl.split("#")[0];
    navigator.clipboard.writeText(`${currentUrlWithoutHash}#${newUrlHash}`);
    setCopySuccess(true);
  }

  const currentStateFromUrl = () => {
    const url = window.location.href;
    try {
      const urlState = urlToUrlState(url);
      return urlState;
    } catch (err: any) {
      console.error(err);
      setError(err);
    }
  };

  return {
    currentStateFromUrl,
    updateUrlState,
    copyShareUrl,
    copySuccess,
    error,
  };
}
