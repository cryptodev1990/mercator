export async function getFileFromUpload(): Promise<File | null> {
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

export const sniff = (df: DataFrame) => {
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
};

const jsTypeToSqliteType = (type: string) => {
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
};

export const base64ToString = (base64: string) => {
  // convert base64 encoded string to string
  // don't use atob because it doesn't work in node
  return Buffer.from(base64, "base64").toString("ascii");
};

export const stringToBase64 = (str: string) => {
  // convert string to base64 encoded string
  return Buffer.from(str).toString("base64");
};

export const getRandomElement = (arr: string[]) => {
  // choose random element from array
  return arr[Math.floor(Math.random() * arr.length)];
};
