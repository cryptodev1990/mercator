import { convertZip, sanitize } from "./utils";

describe("convertZip", () => {
  test("should pad numbers with less than five digits", () => {
    expect(convertZip(1)).toEqual("00001");
  });
});

describe("sanitize", () => {
  test("should return empty dataframes arry and no error without urls or files", async () => {
    expect(await sanitize([])).toEqual([]);
  });
});
