import { JSONLoader, load } from "@loaders.gl/core";
import { CSVLoader } from "@loaders.gl/csv";

const sanitizeColumnNames = (columns: string[]) => {
  // if column names contain an invalid character, throw an error
  const invalidCharacters = [" ", "-", "."];
  for (const col of columns) {
    for (const char of invalidCharacters) {
      if (col.includes(char)) {
        throw new Error(
          `Column name ${col} contains invalid character ${char}`
        );
      }
    }
  }
};

const convertZip = (potentialZip: number) => {
  return potentialZip.toString().padStart(5, "0");
};

const sanitizeData = async (urlsOrFile: (string | File)[]) => {
  const newDfs: DataFrame[] = [];
  for (const path of urlsOrFile) {
    const df: DataFrame = {
      columns: [],
      data: [],
    };

    try {
      if (typeof path === "string" || path instanceof File) {
        df.data = await load(path, [CSVLoader, JSONLoader]);
      } else {
        throw new Error("Unknown file type");
      }
    } catch (err: any) {
      throw err;
    }

    // apply the function to convert any of the data frame records to a string if ZIP is a number
    df.data = df.data.map((row: any) => {
      for (const key of Object.keys(row)) {
        if (
          ["zcta", "zip", "zip_code"].includes(key) &&
          typeof row[key] === "number"
        ) {
          row[key] = convertZip(row[key]);
        }
      }
      return row;
    });

    // We assume the header is properly set in the first row
    df.columns = df.data[0] ? (Object.keys(df.data[0]) as string[]) : [];
    sanitizeColumnNames(df.columns);
    newDfs.push(df);
  }

  if (
    newDfs.length === 1 &&
    (newDfs[0].data.length === 0 || newDfs[0].columns.length === 0)
  ) {
    throw new Error("No data found, please check your file and try again");
  }

  return newDfs;
};

export default sanitizeData;
