export async function getUploadData(): Promise<File | null> {
  const file = await new Promise((resolve) => {
    const input = document.createElement("input");
    input.type = "file";
    // restrict to csv files or json files
    input.accept = ".csv,.json";
    input.onchange = () => {
      resolve(input.files?.[0]);
    };
    input.click();
  });
  if (!file) {
    return null;
  }
  return file as File;
}

export function sanitizeColumnNames(columns: string[]) {
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
}

export function sniff(df: DataFrame) {
  const columns = df.columns;
  const counter: any = {};
  // count the number of any type in first 100 rows
  let i = 0;
  for (const row of df.data) {
    for (const col of columns) {
      const type = typeof row[col];
      if (counter[col]) {
        if (counter[col][type]) {
          counter[col][type] += 1;
        } else {
          counter[col][type] = 1;
        }
      } else {
        counter[col] = {};
        counter[col][type] = 1;
      }
    }
    if (i > 100) {
      break;
    }
    i += 1;
  }

  const types = [];
  for (const col of columns) {
    // set seach column to the most common type
    // if the column name is zip, zip_code, zcta, then the type is string
    if (["zip", "zip_code", "zcta"].includes(col.toLowerCase())) {
      types.push("TEXT");
      continue;
    }
    const type = Object.keys(counter[col]).reduce((a, b) =>
      counter[col][a] > counter[col][b] ? a : b
    );

    types.push(jsTypeToSqliteType(type));
  }

  return types;
}

function jsTypeToSqliteType(type: string) {
  switch (type) {
    case "string":
      return "TEXT";
    case "number":
      return "REAL";
    case "boolean":
      return "INTEGER";
    default:
      return "TEXT";
  }
}

export const convertZip = (potentialZip: number) => {
  return potentialZip.toString().padStart(5, "0");
};