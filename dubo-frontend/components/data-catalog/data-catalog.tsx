import { useRouter } from "next/router";
import Fuse from "fuse.js";
import TitleBlock from "../geomap/title-block";
import { useEffect, useRef, useState, useMemo } from "react";
import Link from "next/link";
import CategoryGrid from "./category-grid";
import { AgGridReact } from "ag-grid-react";

const BACKEND_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL || "https://dubo-api.mercator.tech";

const ENDPOINT = `${BACKEND_URL}/demos/census/variables`;

const CENSUS_SOURCE_URL =
  "https://www.census.gov/data/developers/data-sets/acs-5year.html";

function cleanDescription(description: string) {
  // Remove the word "Estimate" from the description and replace "!!" with " " and replace the final ":"
  return description
    .replace("Estimate!!", "")
    .replace("Total:!!", "")
    .replace(/!!/g, " ")
    .replace(/:$/, "");
}

function linkToVarInCensus(varname: string) {
  if (
    !varname.startsWith("B") &&
    !varname.startsWith("C") &&
    varname !== "ZCTA"
  ) {
    throw new Error("Variable must start with B or C");
  }
  return `https://api.census.gov/data/2021/acs/acs5/variables/${varname}.html`;
}

const DataCatalog = () => {
  const router = useRouter();
  const fuseRef = useRef<Fuse<MetaCensusRecord>>();
  const [searchResults, setSearchResults] = useState<MetaCensusRecord[]>([]);

  const [rowData, setRowData] = useState<object[] | null>(null);
  const columnDefs: { field: keyof MetaCensusRecord; headerName: string }[] =
    useMemo(
      () => [
        { field: "dubo_name", headerName: "Name" },
        {
          field: "label",
          headerName: "Description",
          cellRenderer: ({ value }: { value: string }) =>
            cleanDescription(value),
        },
        { field: "concept", headerName: "Category" },
        {
          field: "name",
          headerName: "Census Source",
          cellRenderer: ({ value }: { value: string }) => (
            <a
              href={linkToVarInCensus(value)}
              target="_blank"
              className="text-blue-500 underline text-sm"
              rel="noreferrer"
            >
              {value}
            </a>
          ),
        },
      ],
      []
    );

  useEffect(() => {
    setRowData(searchResults);
  }, [searchResults]);

  const defaultColDef = useMemo(
    () => ({ sortable: true, filter: true, resizable: true, flex: 1 }),
    []
  );

  useEffect(() => {
    async function createFuse() {
      const data = await fetch(ENDPOINT, {
        headers: {
          "Content-Type": "application/json",
        },
      }).then((res) => res.json());
      fuseRef.current = new Fuse(data, {
        keys: ["name", "dubo_name", "label", "concept"],
      });
      // prime the results so the search results aren't empty
      search("time to work");
    }
    createFuse();
  }, []);

  function search(query: string) {
    if (!fuseRef.current) {
      return [];
    }
    const res = fuseRef.current.search(query);
    const mappedRes = res.map((r) => r.item);
    setSearchResults(mappedRes);
  }

  return (
    <div className="relative border animate-fadeIn500 bg-slate-100 w-screen h-screen">
      <div className="border-b-4 border-black">
        <div className="max-w-5xl mx-auto">
          <TitleBlock zoomThreshold={false} />
          <div className="static float-right">
            <button onClick={() => router.push("/demos/census")}>{"<<"}</button>
          </div>
        </div>
      </div>
      <div className="max-w-5xl mx-auto">
        <div>
          {/* Exposition */}
          <section>
            {/* Copy text - header */}
            <h1 className="text-xl font-bold leading-10 pt-1">Data Catalog</h1>
            <div className="flex flex-row">
              {/* Copy text - body */}

              <div id="copy" className="col-span-5 flex flex-col">
                <p className="text-md leading-4">
                  Below are the variables from the US Census Bureau{"'"}s{" "}
                  <a
                    className="text-blue-500 underline"
                    href={CENSUS_SOURCE_URL}
                    rel="noreferrer"
                  >
                    2021 5-year American Community Survey (ACS)
                  </a>{" "}
                  made available by dubo. There are 350 variables in total.
                </p>
                <br />
                <p className="text-md leading-4">
                  Requests for other data sets or additional variables can be
                  made via our{" "}
                  <Link href={"/feedback"} className="text-blue-500 underline">
                    feedback form
                  </Link>
                  .
                </p>
                <br />
                <p className="text-md leading-4">
                  While you can{"'"}t query these variables directly through
                  dubo, hopefully this gives you an idea of the kind of
                  questions you can ask.
                </p>
                <div className="flex-none my-auto">
                  <h3>Start typing to search</h3>
                  {/* Search bar */}
                  <input
                    className="border border-gray-300 rounded-md w-full p-2 text-lg"
                    placeholder="Variable name to search for..."
                    type="text"
                    onChange={(e) => {
                      search(e.target.value);
                    }}
                  />
                </div>
              </div>
              {/* spacer */}
              {/* Category grid */}
              <div className="ml-6">
                <CategoryGrid onClick={(category) => search(category)} />
              </div>
            </div>
          </section>
          <br />
          <div className="mt-2 ag-theme-alpine" style={{ height: 500 }}>
            <AgGridReact
              defaultColDef={defaultColDef}
              rowData={rowData}
              columnDefs={columnDefs}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default DataCatalog;
