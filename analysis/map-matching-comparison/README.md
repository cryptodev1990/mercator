Map-matching Comparison
------------------------

We visually compare map matching results for routes from

- Historic Vehicle Data Open Data from Cincinnati, Ohio [Source](https://data.cincinnati-oh.gov/Thriving-Neighborhoods/Historic-Vehicle-GPS-Data-Department-of-Public-Ser/jmaw-gcgj)
- Current Year Vehicle History Data from San Francisco [Source](https://data.sfgov.org/Transportation/SFMTA-Transit-Vehicle-Location-History-Current-Yea/x344-v6h6)

First, we look for "noisy" GPS traces.
This would be any trace where a point jumps at a speed of over 40 meters per second.

The Cincinnati data set offers odometer readings, so we can compare the odometer
reading to the map-matched distance. Closest estimate wins.
