#!/usr/bin/env Rscript
# Install dependencies for the GeoLift R package
# These must be available for pygeolift to work
install.packages("remotes", repos='http://cran.us.r-project.org')
remotes::install_github("ebenmichael/augsynth")
remotes::install_github("facebookincubator/GeoLift")
