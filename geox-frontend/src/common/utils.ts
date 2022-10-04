export function findIndex(uuid: string, collection: any): number {
  /**
   * Find index of a UUID in a collection of elements that all have UUIDs
   */
  if (collection === undefined) {
    return -1;
  }
  for (let i = 0; i < collection.length; i++) {
    if (collection[i].uuid === uuid) {
      return i;
    }
  }
  return -1;
}
