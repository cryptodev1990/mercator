import { sanitize } from "../utils";

addEventListener("message", async (event: MessageEvent<any>) => {
  try {
    const dfs = await sanitize(event.data);
    postMessage({ dfs });
  } catch (err) {
    postMessage({ error: err });
  }
});
