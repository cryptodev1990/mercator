import sanitizeData from "./sanitize-data";

describe("sanitizeData", () => {
  test("should return empty dataframes array and no error without urls or files", async () => {
    expect(await sanitizeData([])).toEqual([]);
  });
});
