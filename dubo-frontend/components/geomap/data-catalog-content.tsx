import { useRouter } from "next/router";
import Fuse from "fuse.js";
import { TitleBlock } from "./title-block";
import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import clsx from "clsx";

const BACKEND_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL || "https://dubo-api.mercator.tech";

function cleanDescription(description: string) {
  // Remove the word "Estimate" from the description and replace "!!" with " " and replace the final ":"
  return description
    .replace("Estimate!!", "")
    .replace("Total:!!", "")
    .replace(/!!/g, " ")
    .replace(/:$/, "");
}

const ENDPOINT = `${BACKEND_URL}/demos/census/variables`;

const censusCategories = {
  "Demographic data": {
    search:
      "SEX BY AGE|HISPANIC OR LATINO ORIGIN BY RACE|RACE|TENURE|HOUSEHOLD SIZE BY VEHICLES AVAILABLE|NUMBER OF EARNERS IN FAMILY|POVERTY STATUS IN THE PAST 12 MONTHS BY AGE",
    color: "bg-sky-700",
  },
  "Income and expenses": {
    search:
      "RATIO OF INCOME TO POVERTY LEVEL OF FAMILIES IN THE PAST 12 MONTHS|AGGREGATE EARNINGS IN THE PAST 12 MONTHS|GROSS RENT AS A PERCENTAGE OF HOUSEHOLD INCOME IN THE PAST 12 MONTHS|ANNUAL WATER AND SEWER COSTS|MONTHLY ELECTRICITY COSTS|MORTGAGE STATUS|MORTGAGE STATUS BY AGGREGATE REAL ESTATE TAXES PAID|MEDIAN VALUE",
    color: "bg-amber-500",
  },
  "Housing data": {
    search:
      "AGGREGATE CONTRACT RENT|AGGREGATE GROSS RENT|AGGREGATE NUMBER OF ROOMS|AGGREGATE PRICE ASKED|AGGREGATE VALUE|HOUSE HEATING FUEL|KITCHEN FACILITIES FOR ALL HOUSING UNITS|YEAR STRUCTURE BUILT",
    color: "bg-indigo-800",
  },
  Transportation: {
    search:
      "AGGREGATE NUMBER OF VEHICLES AVAILABLE BY TENURE|AGGREGATE NUMBER OF VEHICLES USED IN COMMUTING BY WORKERS|MEANS OF TRANSPORTATION TO WORK BY INDUSTRY|AGGREGATE TRAVEL TIME TO WORK OF WORKERS|TRAVEL TIME TO WORK",
    color: "bg-indigo-500",
  },
  Education: {
    search:
      "TOTAL FIELDS OF BACHELOR'S DEGREES REPORTED|TYPES OF COMPUTERS IN HOUSEHOLD",
    color: "bg-orange-700",
  },
  Health: {
    search: "ALLOCATION OF MEDICARE COVERAGE",
    color: "bg-yellow-500",
  },
};

const CENSUS_SOURCE_URL =
  "https://www.census.gov/data/developers/data-sets/acs-5year.html";

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

export type MetaCensusRecord = {
  name: string;
  dubo_name: string;
  label: string;
  concept: string | null;
};

const CensusRow = ({ row }: { row: MetaCensusRecord }) => {
  return (
    <div className="flex flex-row w-full py-1">
      <div className="flex-1 break-all inline-block">{row.dubo_name}</div>
      <div className="flex-1 break-words inline-block">
        {cleanDescription(row.label)}
      </div>
      <div className="flex-1 break-words inline-block">{row.concept}</div>
      <div className="flex-1">
        <a
          href={`${linkToVarInCensus(row.name)}`}
          target="_blank"
          className="text-blue-500 underline text-sm"
          rel="noreferrer"
        >
          {row.name}
        </a>
      </div>
    </div>
  );
};

const CensusCategory = ({
  category,
  color,
  onClick,
}: {
  category: string;
  color: string;
  onClick: () => void;
}) => {
  // A square containing the name of the category
  // On click, we place the category name in the search bar
  // and then we filter the results
  return (
    <button
      onClick={onClick}
      className={clsx(
        "h-32 w-32 text-slate-100 cursor-pointer mb-1 mr-1 rounded-xl",
        "flex flex-col justify-start items-center overflow-hidden",
        "hover:bg-sky-500",
        color
      )}
    >
      <div
        className={clsx(
          "text-left px-11/24",
          "text-md font-sans2 leading-none my-auto"
        )}
      >
        {category}
      </div>
    </button>
  );
};

const CategoryGrid = ({ onClick }: { onClick: (category: string) => void }) => {
  // A grid of categories
  return (
    <>
      <div className="grid grid-cols-3 w-[25rem]">
        {Object.keys(censusCategories).map((category) => (
          <CensusCategory
            category={category}
            // @ts-ignore
            color={censusCategories[category].color}
            key={category}
            // @ts-ignore
            onClick={() => onClick(censusCategories[category].search)}
          />
        ))}
      </div>
    </>
  );
};

export const DataCatalogContent = () => {
  const router = useRouter();
  const fuseRef = useRef<Fuse<MetaCensusRecord>>();
  const [searchResults, setSearchResults] = useState<MetaCensusRecord[]>([]);

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
    <div className="relative border animate-fadeIn500 bg-slate-100 w-screen h-fit">
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
          <div className="flex flex-col">
            {searchResults.length > 0 && (
              <div
                key={0}
                className="flex flex-row bg-blue-500 py-4 p-2 text-slate-50 rounded"
              >
                <div className="flex-1 font-extrabold">Name</div>
                <div className="flex-1 font-extrabold">Description</div>
                <div className="flex-1 font-extrabold">Category</div>
                <div className="flex-1 font-extrabold">Census Source</div>
              </div>
            )}
            <div className="p-2">
              {searchResults.length > 0 &&
                searchResults.map(
                  (r, i) => i < 50 && <CensusRow key={r.name + i} row={r} />
                )}
            </div>
            {searchResults.length > 50 && (
              <div className="text-sm text-gray-500 ">
                Showing first 50 results
                <br />
                <br />
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
