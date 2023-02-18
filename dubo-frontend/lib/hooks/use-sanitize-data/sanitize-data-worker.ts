import sanitizeData from "./sanitize-data";

addEventListener("message", async (event: MessageEvent<any>) => {
  try {
    const dfs = await sanitizeData(event.data);
    postMessage({ dfs });
  } catch (err) {
    postMessage({ error: err });
  }
});
