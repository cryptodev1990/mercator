import { renderHook, act } from "@testing-library/react";
import usePrepareData from "./use-prepare-data";

describe("usePrepareData", () => {
  test("should return empty dataframes arry and no error without urls or files", async () => {
    let preparedData;

    await act(async () => {
      preparedData = await renderHook(() =>
        usePrepareData({ selectedData: null, urlsOrFile: [] })
      );
    });

    // @ts-ignore
    const received = preparedData?.result?.current;

    expect(received.dfs).toEqual([]);
    expect(received.error).toEqual(null);
  });
});
