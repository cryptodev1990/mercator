import { useEffect, useMemo, useRef, useState } from "react";
import clsx from "clsx";
import { FaCheck, FaShareAltSquare } from "react-icons/fa";

import useCensus from "../../lib/hooks/census/use-census";
import useCensusAutocomplete from "../../lib/hooks/census/use-census-autocomplete";
import { SearchBar } from "../search-bar";
import { usePalette } from "../../lib/hooks/scales/use-palette";
import { ThemeProvider, useTheme } from "../../lib/hooks/census/use-theme";
import { EXAMPLES } from "../../lib/hooks/census/use-first-time-search";
import { nab } from "../../lib/utils";
import { useUrlState } from "../../lib/hooks/url-state/use-url-state";

import Legend, { ColumnSelector } from "./legend";
import { DeckMap } from "./deck-map";
import { Tooltip } from "./tooltip";
import { LoadingSpinner } from "./loading-spinner";
import { ErrorBox } from "./error-box";
import styles from "./geomap.module.css";
import TitleBlock from "./title-block";
import { SQLButtonBank, ShowInPlaceOptionsType } from "./sql-button-bank";
import SQLBar from "./sql-bar";

const GeoMap = () => {
  const { theme } = useTheme();
  const [query, setQuery] = useState(
    !window.location.hash ? nab(EXAMPLES) : ""
  );
  const { currentStateFromUrl, updateUrlState, copyShareUrl, copySuccess } =
    useUrlState();
  const [localQuery, setLocalQuery] = useState(query);
  const [selectedZcta, setSelectedZcta] = useState("");
  const [selectedColumn, setSelectedColumn] = useState("");
  const [zoomThreshold, setZoomThreshold] = useState(false);
  const [label, setLabel] = useState<string | null>(null);
  const deckContainerRef = useRef<HTMLDivElement | null>(null);
  const [showInPlace, setShowInPlace] = useState<ShowInPlaceOptionsType>(null);
  const [showErrorBox, setShowErrorBox] = useState(false);

  useEffect(() => {
    if (query) updateUrlState({ userQuery: query });
  }, [query]);

  useEffect(() => {
    // Load from URL hash
    const urlState = currentStateFromUrl();
    if (urlState?.userQuery) {
      setQuery(urlState.userQuery);
      setLocalQuery(urlState.userQuery);
    }
  }, []);

  useEffect(() => {
    // Open census data catalog in new tab
    if (showInPlace === "data_catalog") {
      // navigate to data catalog using router
      window.open("/demos/census/data-catalog", "_blank");
    }
  }, [showInPlace]);

  const {
    data: { header, lookup: zctaLookup, generatedSql },
    isLoading,
    error,
  } = useCensus({
    query,
  });
  const { data: autocompleteSuggestions } = useCensusAutocomplete({
    text: localQuery,
  });

  const dataVector = useMemo(() => {
    if (!zctaLookup) return [];
    const vals = Object.values(zctaLookup).map((d: any) =>
      Number(d[selectedColumn])
    );
    return vals;
  }, [zctaLookup, selectedColumn]);

  const {
    colors,
    breaks,
    scale,
    setPaletteName,
    rotateScaleType,
    isRatio,
    scaleType,
  } = usePalette({
    vec: dataVector,
  });

  useEffect(() => {
    if (error) {
      setShowErrorBox(true);
      console.error("error", error);
    }
  }, [error]);

  useEffect(() => {
    if (isLoading) return;
    if (!header) return;
    if (selectedColumn) return;
    // if there's no selected column, select the first one
    // Line of code is un-intuitively important
    // At least one column must be selected for the map to render
    setSelectedColumn(header[0]);
  }, [header, selectedColumn]);

  return (
    <div className={clsx(styles.geomapContainer, theme.fontColor)}>
      <div className="w-full h-full relative" ref={deckContainerRef}>
        <div
          className={clsx(
            "z-10 w-full",
            "relative max-w-5xl rounded-md mx-auto sm:p-3",
            "pointer-events-none"
          )}
        >
          <TitleBlock zoomThreshold={zoomThreshold} />
          <div className="pointer-events-auto mb-3">
            <SearchBar
              setShowErrorBox={setShowErrorBox}
              value={localQuery}
              onChange={(text) => setLocalQuery(text)}
              onEnter={(newSearchQuery) => {
                if (newSearchQuery) {
                  setQuery(newSearchQuery);
                } else {
                  setQuery(localQuery);
                }
                setSelectedColumn("");
              }}
              autocompleteSuggestions={
                autocompleteSuggestions?.suggestions ?? []
              }
            />
            <div className="flex flex-row w-full">
              <SQLButtonBank
                setShowInPlace={setShowInPlace}
                showInPlace={showInPlace}
              />
              {showInPlace === "generated_sql" && (
                <SQLBar
                  generatedSql={generatedSql}
                  setShowInPlace={setShowInPlace}
                  theme={theme.theme}
                />
              )}
              {/*Share button*/}
              <button
                className="my-1 flex items-center justify-center w-10 h-10 ml-auto text-white bg-gray-500 rounded-md group"
                onClick={() => {
                  copyShareUrl();
                }}
              >
                <div className="absolute z-50 flex items-center justify-center w-10 h-10 text-white bg-gray-500 rounded-md">
                  {copySuccess ? (
                    <span className="text-xs transition transform duration-300 ease-in-out opacity-0 group-hover:opacity-100 group-hover:scale-100">
                      Copied!
                    </span>
                  ) : (
                    <FaShareAltSquare />
                  )}
                </div>
              </button>
            </div>
          </div>
          {error && (
            <div className="flex justify-center pointer-events-auto">
              <ErrorBox
                showErrorBox={showErrorBox}
                setShowErrorBox={setShowErrorBox}
                error={error}
                onDismiss={() => {
                  setLocalQuery("");
                  setQuery("");
                  setSelectedColumn("");
                }}
              />
            </div>
          )}
        </div>

        <LoadingSpinner isLoading={isLoading} />
        {/* legend */}
        <div className="absolute bottom-0 left-0 z-50 m-2">
          {header.length > 0 && (
            <Legend
              colors={colors}
              text={breaks}
              isRatio={isRatio}
              setPaletteName={setPaletteName}
              scaleType={scaleType}
              onScaleTextClicked={rotateScaleType}
              label={label}
              setLabel={setLabel}
            >
              <ColumnSelector
                columns={header}
                selectedColumn={selectedColumn}
                setSelectedColumn={setSelectedColumn}
              />
            </Legend>
          )}
        </div>

        {/* tooltip */}
        {zctaLookup && (
          <Tooltip
            isRatio={isRatio}
            label={label}
            zctaLookup={zctaLookup}
            selectedColumn={selectedColumn}
            selectedZcta={selectedZcta}
          />
        )}
      </div>
      <DeckMap
        zctaLookup={zctaLookup}
        selectedColumn={selectedColumn}
        selectedZcta={selectedZcta}
        setSelectedZcta={setSelectedZcta}
        deckContainerRef={deckContainerRef}
        colors={colors}
        scale={scale}
        baseMap={theme.baseMap}
        onZoom={(zoom: number) => {
          if (zoom > 4) {
            setZoomThreshold(true);
          } else {
            setZoomThreshold(false);
          }
        }}
      />
    </div>
  );
};

const GeoMapWithTheme = () => {
  return (
    <ThemeProvider>
      <GeoMap />
    </ThemeProvider>
  );
};

export default GeoMapWithTheme;
