// @ts-ignore
import { KalmanFilter } from "kalman-filter";
import { length } from "@turf/turf";

function deg2rad(deg: any) {
  return deg * (Math.PI / 180);
}

function getHaversineDistance(p0: any, p1: any) {
  const [lon0, lat0] = p0;
  const [lon1, lat1] = p1;
  const R = 6371; // Radius of the earth in km
  const dLat = deg2rad(lat1 - lat0); // deg2rad below
  const dLon = deg2rad(lon1 - lon0);
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(deg2rad(lat0)) *
      Math.cos(deg2rad(lat1)) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  const d = R * c; // Distance in km
  return d * 0.621371;
}

export function smoothWithAverage(coords: number[][]) {
  const output = [];
  for (let i = 1; i < coords.length - 1; i++) {
    const [x, y] = coords[i];
    const [x1, y1] = coords[i + 1];
    if (getHaversineDistance([x, y], [x1, y1]) > 0.5) {
      i++;
      i++;
    }
    output.push([x, y]);
  }
  return [coords[0], ...output, coords[coords.length - 1]];
}

const timeStep = 0.5;

const huge = 1e8;

const kFilter = new KalmanFilter({
  observation: {
    name: "sensor",
    sensorDimension: 2,
  },
  dynamic: {
    init: {
      // We just use random-guessed values here that seems reasonable
      mean: [[1], [1], [1], [0], [0], [0]],
      // We init the dynamic model with a huge covariance cause we don't
      // have any idea where my modeled object before the first observation is located
      covariance: [
        [huge, 0, 0, 0, 0, 0],
        [0, huge, 0, 0, 0, 0],
        [0, 0, huge, 0, 0, 0],
        [0, 0, 0, huge, 0, 0],
        [0, 0, 0, 0, huge, 0],
        [0, 0, 0, 0, 0, huge],
      ],
    },
    // Corresponds to (x, y, z, vx, vy, vz)
    dimension: 6,
    // This is a constant-speed model on 3D : [ [Id , timeStep*Id], [0, Id]]
    transition: [
      [1, 0, 0, timeStep, 0, 0],
      [0, 1, 0, 0, timeStep, 0],
      [0, 0, 1, 0, 0, timeStep],
      [0, 0, 0, 1, 0, 0],
      [0, 0, 0, 0, 1, 0],
      [0, 0, 0, 0, 0, 1],
    ],
    // Diagonal covariance for independant variables
    // since timeStep = 0.1,
    // it makes sense to consider speed variance to be ~ timeStep^2 * positionVariance
    covariance: [1, 1, 1, 0.01, 0.01, 0.01], // equivalent to diag([1, 1, 1, 0.01, 0.01, 0.01])
  },
});

export const smoothWithKalman = (coords: number[][]) => {
  const smoothedCoordinates = kFilter.filterAll(coords);
  return smoothedCoordinates;
};
