/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Feature } from "./Feature";

export type GeoShapeCreate = {
  uuid?: any;
  /**
   * Name of the shape
   */
  name?: string;
  /**
   * GeoJSON representation of the shape
   */
  geojson: Feature;
  /**
   * Namespace id.
   */
  namespace?: string;
};
