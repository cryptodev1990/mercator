# Save GeoLift example data to CSVs
library("GeoLift")
library("readr")
(data("GeoLift_Test", package="GeoLift"))
write_csv(GeoLift_Test, "GeoLift_Test.csv")
(data("GeoLift_PreTest", package="GeoLift"))
write_csv(GeoLift_PreTest, "GeoLift_PreTest.csv")
