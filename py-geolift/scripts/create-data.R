#!/bin/env Rscript
# Save R package data to formats readable by the python package
library("readr")
library("fs")
outdir <- fs::dir_create("./pygeolift/data")
data("GeoLift_PreTest", package="GeoLift")
write_csv(GeoLift_PreTest, fs::path(outdir, "GeoLift_PreTest.csv"), na="")
data("GeoLift_Test", package="GeoLift")
write_csv(GeoLift_Test, fs::path(outdir, "GeoLift_Test.csv"), na="")
# GeoLift_Test