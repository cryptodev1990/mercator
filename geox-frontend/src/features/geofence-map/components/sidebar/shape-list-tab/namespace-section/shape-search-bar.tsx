import { useGetNamespaces } from "features/geofence-map/hooks/use-openapi-hooks";
import Fuse from "fuse.js";
import { useContext, useEffect, useRef, useState } from "react";
import { toast } from "react-hot-toast";
import { CgSearch } from "react-icons/cg";
import { GeoShapeMetadata } from "../../../../../../client";
import { useDebounce } from "../../../../../../hooks/use-debounce";
import { SearchContext } from "../../../../contexts/search-context";
import { useShapes } from "../../../../hooks/use-shapes";

export const ShapeSearchBar = () => {
  // persist fuse instance
  const fuseRef = useRef<Fuse<GeoShapeMetadata>>(null);
  const { setActiveNamespaceIDs } = useShapes();
  const { data: namespaces } = useGetNamespaces();
  const [searchTerm, setSearchTerm] = useState<string | null>(null);
  const { setSearchResults } = useContext(SearchContext);
  const debouncedSearchTerm: string = useDebounce(searchTerm, 200);

  useEffect(() => {
    // filter to unique property keys
    if (namespaces) {
      const allUniquePropertyKeys = namespaces
        ?.flatMap((x) => x.shapes ?? [])
        .reduce(
          (acc, shape) => [
            ...acc,
            ...Object.keys(shape.properties).filter(
              (key) => !acc.includes(key)
            ),
          ],
          [] as string[]
        );
      const fuse = new Fuse(
        namespaces?.flatMap((x) => x.shapes ?? []),
        {
          keys: [
            ...allUniquePropertyKeys.map((x) => "properties." + x),
            "name",
          ],
          threshold: 0.3,
          distance: 100,
        }
      );
      // @ts-ignore
      fuseRef.current = fuse;
    }
  }, [namespaces]);

  useEffect(() => {
    if (!fuseRef.current || !debouncedSearchTerm || !namespaces) {
      return;
    }
    const results = debouncedSearchTerm
      ? fuseRef.current.search(debouncedSearchTerm)
      : namespaces.flatMap((x) => x.shapes ?? []).map((x) => ({ item: x }));
    if (results.length > 0) {
      // set new activeNamespaceIDs
      let namespaceIds = new Set(results.map((x) => x.item.namespace_id));
      const newActives = namespaces.filter((namespace) =>
        namespaceIds.has(namespace.id)
      );
      setActiveNamespaceIDs(newActives.map((x) => x.id));
      setSearchResults(results.map((x) => x.item.uuid));
    } else {
      toast.remove();
      toast("No results found", { icon: "????" });
      setSearchResults([]);
    }
  }, [debouncedSearchTerm]);

  return (
    <div className="w-full flex flex-row justify-start align-baseline pl-1 pr-2 py-3">
      <CgSearch size={20} className="text-gray-400 mx-2 translate-y-2" />
      <input
        className={`w-full h-8 ml-1 mr-2 rounded text-slate-50
        p-2
        bg-slate-700 border border-gray-300 focus:border-gray-400 focus:outline-none"
        `}
        type="text"
        placeholder="Search shapes"
        value={searchTerm || ""}
        onChange={(e) => {
          if (e.target.value === "") {
            setSearchResults([]);
          }
          setSearchTerm(e.target.value);
        }}
      ></input>
    </div>
  );
};
