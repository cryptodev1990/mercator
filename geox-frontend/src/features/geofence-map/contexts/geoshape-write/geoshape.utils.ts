import { NamespaceResponse } from "../../../../client";

export function namespacesAndShapes(nrs: NamespaceResponse[]) {
  /**
   * @param nrs: NamespaceResponse[]
   * @returns {namespaces: Namespace[], shapes: Shape[]}
   *
   * Unnests the namespaces and shapes from the NamespaceResponse[]
   */
  const shapes = [];
  const namespaces: NamespaceResponse[] = [];
  for (const nr of nrs) {
    namespaces.push({
      name: nr.name,
      id: nr.id,
      created_at: nr.created_at,
      updated_at: nr.updated_at,
      organization_id: nr.organization_id,
      is_default: nr.is_default,
      properties: nr.properties,
    });
    if (!nr.shapes) {
      continue;
    }
    for (const shape of nr.shapes) {
      shapes.push(shape);
    }
  }

  return {
    namespaces,
    shapes,
  };
}
