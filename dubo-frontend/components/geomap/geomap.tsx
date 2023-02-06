import { useEffect, useMemo, useRef, useState } from "react";
import useCensus from "../../lib/hooks/census/use-census";
import Legend, { ColumnSelector } from "./legend";
import useCensusAutocomplete from "../../lib/hooks/census/use-census-autocomplete";
import { SearchBar } from "../search-bar";
import { usePalette } from "../../lib/hooks/scales/use-palette";
import { DeckMap } from "./deck-map";
import { Tooltip } from "./tooltip";
import { DownloadCSVButton } from "./download-csv-button";
import { LoadingSpinner } from "./loading-spinner";
import { ErrorBox } from "./error-box";

import styles from "./geomap.module.css";
import clsx from "clsx";
import { ThemeProvider, useTheme } from "../../lib/hooks/census/use-theme";
import { EXAMPLES } from "../../lib/hooks/census/use-first-time-search";
import { TitleBlock } from "./title-block";

const nab = (arr: string[]) => {
  // choose random element from array
  return arr[Math.floor(Math.random() * arr.length)];
};

const GeoMap = () => {
  const { theme } = useTheme();
  const [query, setQuery] = useState(nab(EXAMPLES));
  const [localQuery, setLocalQuery] = useState(query);
  const [selectedZcta, setSelectedZcta] = useState("");
  const [selectedColumn, setSelectedColumn] = useState("");
  const [hideTitleBlock, setHideTitleBlock] = useState(false);
  const deckContainerRef = useRef<HTMLDivElement | null>(null);

  const {
    data: { header, lookup: zctaLookup },
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
    const vals = Object.values(zctaLookup).map((d: any) => +d[selectedColumn]);
    return vals;
  }, [zctaLookup, selectedColumn]);

  const { colors, breaks, scale, setPaletteName, rotateScaleType, isRatio } =
    usePalette({
      vec: dataVector,
    });

  useEffect(() => {
    if (error) console.error("error", error);
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
            "z-10 w-full p-5 ",
            "relative max-w-5xl rounded-md mx-auto p-3",
            "pointer-events-none"
          )}
        >
          <TitleBlock hideTitleBlock={hideTitleBlock} />
          <div className="pointer-events-auto">
            <SearchBar
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
          </div>
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
              onScaleTextClicked={rotateScaleType}
            >
              <ColumnSelector
                columns={header}
                selectedColumn={selectedColumn}
                setSelectedColumn={setSelectedColumn}
              />
            </Legend>
          )}
        </div>
        {error && (
          <div className="relative top-[50%] flex flex-col mx-auto z-50 bg-orange-500">
            <ErrorBox
              error={error}
              onDismiss={() => {
                setLocalQuery("");
                setQuery("");
                setSelectedColumn("");
              }}
            />
          </div>
        )}
        {/* download as csv */}
        {header.length > 0 && <DownloadCSVButton />}
        {/* tooltip */}
        {zctaLookup && (
          <Tooltip
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
            setHideTitleBlock(true);
          } else {
            setHideTitleBlock(false);
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
