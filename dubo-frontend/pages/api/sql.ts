// Next.js API route support: https://nextjs.org/docs/api-routes/introduction
import type { NextApiRequest, NextApiResponse } from "next";

type Data = {
  name: string;
};

const PROMISER_URL =
  "https://xmwdyaolhaobykjycchu.supabase.co/storage/v1/object/public/landing-page/jswasm/sqlite3-worker1-promiser.js?t=2023-01-12T23%3A22%3A48.959Z";

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<Data>
) {
  // https://developer.chrome.com/blog/sqlite-wasm-in-the-browser-backed-by-the-origin-private-file-system/
  const response = await fetch(PROMISER_URL, {
    method: "GET",
    headers: {
      "Content-Type": "application/wasm",
    },
  });
  const data = await response.arrayBuffer();
  const data2 = new Uint8Array(data);
  res.setHeader("Content-Type", "application/wasm");
  res.write(data2);
  res.end();
}
