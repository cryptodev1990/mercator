import { GeoShape, GeoShapeCreate } from "../../../../client";

export type ShapeEditType = "CREATE" | "UPDATE" | "DELETE";
export type ShapeEditRecord = {
  type: ShapeEditType;
  shape: GeoShape | GeoShapeCreate;
  editNumber: number;
};

/**
 * Tracks the set of shapes that have been created, updated, or deleted.
 * We use this for
 * 1) hiding data from the deck tiles that have been deleted (you'll see this in the MVTLayer as well as the deck.gl tooltip)
 * 2) keeping a separate copy of the data that has been updated, purely locally
 *
 * In the future, I imagine we'll use this for undo/redo as well.
 *
 * Results from mutations here are immutable
 *
 */
export class ShapeWriteLog {
  private log: ShapeEditRecord[] = [];
  private deletedSet = new Set<string>();
  private updatedSet = new Set<string>();
  private createdSet = new Set<string>();

  public constructor() {
    this.log = [];
    this.deletedSet = new Set();
    this.updatedSet = new Set();
    this.createdSet = new Set();
  }

  public immutableAppend({
    shape,
    type,
  }: {
    shape: GeoShape | GeoShapeCreate;
    type: ShapeEditType;
  }): ShapeWriteLog {
    const newLog = new ShapeWriteLog();
    newLog.log = this.log.slice();
    newLog.log.push({ type, shape, editNumber: newLog.log.length });
    switch (type) {
      case "CREATE":
        newLog.createdSet = new Set(this.createdSet);
        // this is a new shape at the time of creation, so it won't have a UUID
        if ((shape as GeoShape).uuid) {
          newLog.createdSet.add((shape as GeoShape).uuid);
        }
        break;
      case "UPDATE":
        newLog.updatedSet = new Set(this.updatedSet);
        newLog.updatedSet.add((shape as GeoShape).uuid);
        break;
      case "DELETE":
        newLog.deletedSet = new Set(this.deletedSet);
        newLog.deletedSet.add((shape as GeoShape).uuid);
        break;
    }
    return newLog;
  }

  public has(shapeUuid: string) {
    return (
      this.createdSet.has(shapeUuid) ||
      this.updatedSet.has(shapeUuid) ||
      this.deletedSet.has(shapeUuid)
    );
  }

  public isDeleted(shapeUuid: string) {
    return this.deletedSet.has(shapeUuid);
  }

  public isUpdated(shapeUuid: string) {
    return this.updatedSet.has(shapeUuid);
  }

  public immutablePop() {
    const newLog = new ShapeWriteLog();
    newLog.log = this.log.slice(0, this.log.length - 1);
    switch (this.log[this.log.length - 1].type) {
      case "CREATE":
        newLog.createdSet = new Set(this.createdSet);
        const { shape } = this.log[this.log.length - 1];
        newLog.createdSet.delete((shape as GeoShape).uuid);
        break;
      case "UPDATE":
        newLog.updatedSet = new Set(this.updatedSet);
        const { shape: updatedShape } = this.log[this.log.length - 1];
        newLog.updatedSet.delete((updatedShape as GeoShape).uuid);
        break;
      case "DELETE":
        newLog.deletedSet = new Set(this.deletedSet);
        const { shape: deletedShape } = this.log[this.log.length - 1];
        newLog.deletedSet.delete((deletedShape as GeoShape).uuid);
        break;
    }
    return newLog;
  }
}
