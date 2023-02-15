import { convertZip } from "./utils";

describe("convertZip", () => {
  test("should pad numbers with less than five digits", () => {
    expect(convertZip(1)).toEqual("00001");
  });
});
