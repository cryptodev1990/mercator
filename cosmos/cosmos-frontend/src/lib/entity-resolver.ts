import { TAILWIND_COLORS } from "./colors";

export interface EntityResolver {
  hr: string;
  mr: string;
  fill: string;
  desc: string;
}

export const ENTITY_RESOLVER: EntityResolver[] = [
  {
    hr: "Category",
    mr: "category",
    fill: TAILWIND_COLORS[3].hex,
    desc: "A category is a broad grouping of entities. For example, a category might be a type of business, such as a restaurant or a hotel.",
  },
  {
    hr: "POI",
    mr: "named_place",
    fill: TAILWIND_COLORS[0].hex,
    desc: "A point of interest (POI) is a specific location. For example, a POI might be a specific restaurant or hotel, or a named place like a city.",
  },
  {
    hr: "Rough match",
    mr: "fuzzy",
    fill: TAILWIND_COLORS[2].hex,
    desc: "A rough match is a fuzzy match of a string to a category or POI. For example, a rough match might be a string that contains a category or POI name, but is not an exact match.",
  },
];
