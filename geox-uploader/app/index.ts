import "@loaders.gl/polyfills";

import express from "express";
import cors from "cors";
import morgan from "morgan";
import { parse } from "@loaders.gl/core";

import { ZipLoader } from "@loaders.gl/zip";

import { CSVLoader } from "@loaders.gl/csv";
import { ParquetLoader } from "@loaders.gl/parquet";
import { GPXLoader, KMLLoader, TCXLoader } from "@loaders.gl/kml";
import { JSONLoader } from "@loaders.gl/json";
import { ExcelLoader } from "@loaders.gl/excel";
import { lookup } from "mime-types";
import fileUpload from "express-fileupload";

import { handleShapefile } from "./shp";


const loaders = [
  CSVLoader,
  ZipLoader,
  ParquetLoader,
  GPXLoader,
  KMLLoader,
  TCXLoader,
  JSONLoader,
  ExcelLoader,
];

const app = express();

app.use(morgan('common'));
app.use(cors());

app.use(
  fileUpload({
    createParentPath: true,
  })
);

// Deny anything larger than a 20MB upload
const BYTE_LIMIT = 20000000;

app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

async function unzip(buffer: any): Promise<any> {
  return await parse(buffer, ZipLoader);
}

app.get("/", (req, res) => {
  res.send("Plane and simple - Copyright Mercator, 2022");
});

app.get("/health", (req, res) => {
  res.send("OK");
});

app.post("/upload", async (req, res) => {
  try {
    if (!req.files) {
      res.send({
        status: "failed",
        message: "No file uploaded",
      });
    } else {
      let file = req.files.data;

      const buffer = (file as any).data;

      if (Buffer.byteLength(buffer) > BYTE_LIMIT) {
        res.send({
          status: "failed",
          message: "Uploads are capped at 20MB.",
        });
        return;
      }

      const mimeType = lookup((file as any).name);
      if (mimeType === false) {
        throw new Error("Unknown mimetype");
      }

      let data;

      if (mimeType === "application/zip") {
        const unzipped = await unzip(buffer);
        data = await handleShapefile(unzipped);
        data = data.data;
      } else {
        data = await parse(buffer, loaders, { mimeType });
      }

      res.send({
        status: "success",
        data,
      });
    }
  } catch (err: any) {
    res.send({
      status: "failed",
      message: err.message,
    });
  }
});

const port = process.env.PORT || 8080;

app.listen(port, () => console.log(`Server started on port ${port}`));
