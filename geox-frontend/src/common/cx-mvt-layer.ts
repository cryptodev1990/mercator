import type { BinaryFeatures } from "@loaders.gl/schema";

import { MVTLayer } from "@deck.gl/geo-layers";
import { Feature } from "../client";
import { MVTLayerProps } from "@deck.gl/geo-layers/mvt-layer/mvt-layer";

function __uuid(feature: Feature) {
  return feature.properties.__uuid;
}

export class TileCache implements TileCacheInterface {
  // Lookup from tile key (x, y, z} to features
  private cache: { [key: string]: Feature[] } = {};
  // lookup from shape UUID collection of tile keys containing that shape
  private reverseMap: { [shapeUuid: string]: Set<string> } = {};
  private numFeatures: number = 0;

  get(key: string): Feature[] | undefined {
    return this.cache[key];
  }

  set(key: string, value: Feature[]): void {
    if (this.numFeatures > 10000) {
      this.clear();
    }
    for (const feature of value) {
      this.numFeatures++;
      if (!this.reverseMap[__uuid(feature)]) {
        this.reverseMap[__uuid(feature)] = new Set();
      }
      this.reverseMap[__uuid(feature)].add(key);
    }
    this.cache[key] = value;
  }

  clearForFeatures(featureUuids: string[]): number {
    let numCleared = 0;
    for (const uuid of featureUuids) {
      if (!this.reverseMap[uuid]) {
        continue;
      }
      // remove all tiles that contain this feature
      for (const key of this.reverseMap[uuid].keys()) {
        delete this.cache[key];
      }
      // remove all references to this feature
      delete this.reverseMap[uuid];
      numCleared++;
    }
    this.numFeatures -= numCleared;
    return numCleared;
  }

  clearTileByKeys(keys: string[]): number {
    console.log(keys);
    let numCleared = 0;
    for (const key of keys) {
      if (this.has(key)) {
        delete this.cache[key];
        numCleared++;
      }
    }
    this.numFeatures -= numCleared;
    return numCleared;
  }

  clear(): void {
    this.numFeatures = 0;
    this.cache = {};
  }

  has(key: string): boolean {
    return key in this.cache;
  }
}

interface TileCacheInterface {
  get(key: string): Feature[] | undefined;
  set(key: string, value: Feature[]): void;
  clear(): void;
  has(key: string): boolean;
}

const defaultProps = {
  cache: null,
};

export type CxMVTLayerProps<DataT = any> = _CxMVTLayerProps &
  MVTLayerProps<DataT>;

type _CxMVTLayerProps = {
  cache: TileCacheInterface;
};

export class CxMVTLayer<ExtraProps = {}> extends MVTLayer<
  BinaryFeatures,
  Required<CxMVTLayerProps> & ExtraProps
> {
  static layerName = "CxMVTLayer";
  static defaultProps = defaultProps;

  getTileData(tile: any) {
    // @ts-ignore
    const { cache } = this.props;
    const CACHE_KEY = `${tile.x}-${tile.y}-${tile.z}`;
    if (cache.has(CACHE_KEY)) {
      return cache.get(CACHE_KEY);
    }

    try {
      const res = super.getTileData(tile).then((data: Feature[]) => {
        cache.set(CACHE_KEY, data);
        return data;
      });
      return res;
    } catch (e) {
      return [];
    }
  }
  renderSubLayers(props: any) {
    return super.renderSubLayers(props);
  }
}
