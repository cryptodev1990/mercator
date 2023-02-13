import CensusCategory from "./census-category";

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

const CategoryGrid = ({ onClick }: { onClick: (category: string) => void }) => {
  // A grid of categories
  return (
    <>
      <div className="flex flex-wrap gap-1">
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

export default CategoryGrid;
