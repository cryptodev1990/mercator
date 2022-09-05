"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
require("@loaders.gl/polyfills");
const express_1 = __importDefault(require("express"));
const cors_1 = __importDefault(require("cors"));
const core_1 = require("@loaders.gl/core");
const zip_1 = require("@loaders.gl/zip");
const csv_1 = require("@loaders.gl/csv");
const parquet_1 = require("@loaders.gl/parquet");
const kml_1 = require("@loaders.gl/kml");
const json_1 = require("@loaders.gl/json");
const excel_1 = require("@loaders.gl/excel");
const mime_types_1 = require("mime-types");
const express_fileupload_1 = __importDefault(require("express-fileupload"));
const shp_1 = require("./shp");
// Produce JSON from
// zipped shapefile directories
// Parquet
// GPX
// KML
// TCX
// Excel
const loaders = [
    csv_1.CSVLoader,
    zip_1.ZipLoader,
    parquet_1.ParquetLoader,
    kml_1.GPXLoader,
    kml_1.KMLLoader,
    kml_1.TCXLoader,
    json_1.JSONLoader,
    excel_1.ExcelLoader,
];
const app = (0, express_1.default)();
app.use((0, cors_1.default)());
app.use((0, express_fileupload_1.default)({
    createParentPath: true,
}));
// Deny anything larger than a 20MB upload
const BYTE_LIMIT = 20000000;
app.use((0, cors_1.default)());
app.use(express_1.default.json());
app.use(express_1.default.urlencoded({ extended: true }));
app.use(express_1.default.json());
app.use(express_1.default.urlencoded({ extended: true }));
function unzip(buffer) {
    return __awaiter(this, void 0, void 0, function* () {
        return yield (0, core_1.parse)(buffer, zip_1.ZipLoader);
    });
}
app.post("/upload", (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    try {
        if (!req.files) {
            res.send({
                status: "failed",
                message: "No file uploaded",
            });
        }
        else {
            let file = req.files.data;
            const buffer = file.data;
            if (Buffer.byteLength(buffer) > BYTE_LIMIT) {
                res.send({
                    status: "failed",
                    message: "Uploads are capped at 20MB.",
                });
                return;
            }
            const mimeType = (0, mime_types_1.lookup)(file.name);
            if (mimeType === false) {
                throw new Error("Unknown mimetype");
            }
            let data;
            if (mimeType === "application/zip") {
                const unzipped = yield unzip(buffer);
                data = yield (0, shp_1.handleShapefile)(unzipped);
                data = data.data;
            }
            else {
                data = yield (0, core_1.parse)(buffer, loaders, { mimeType });
            }
            res.send({
                status: "success",
                data,
            });
        }
    }
    catch (err) {
        res.send({
            status: "failed",
            message: err.message,
        });
    }
}));
const port = process.env.PORT || 8080;
app.listen(port, () => console.log(`Server started on port ${port}`));
