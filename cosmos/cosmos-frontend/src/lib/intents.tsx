export type Intent = {
  humanName: string;
  name: string;
  description: string;
  slots: Slot[];
};

export type Slot = {
  humanName: string;
  name:
    | "any"
    | "place"
    | "time"
    | "distance"
    | "thing"
    | "modality"
    | "locator";
  type: "any" | "string" | "number" | "boolean";
};

const PLACE_SLOT: Slot = {
  humanName: "Place",
  name: "place",
  type: "string",
};

const LOCATOR_SLOT: Slot = {
  humanName: "Preposition",
  name: "locator",
  type: "string",
};

export const INTENTS: Intent[] = [
  {
    humanName: "Find a place",
    name: "find",
    description: "Find a place",
    slots: [PLACE_SLOT],
  },
  {
    humanName: "Find a place",
    name: "find in location",
    description: "Find all places in a location",
    slots: [PLACE_SLOT, LOCATOR_SLOT, PLACE_SLOT],
  },
  // {
  //   humanName: "Draw a radius or travel time",
  //   name: "bufffer location",
  //   description: "Find all places in a location",
  //   slots: [PLACE_SLOT, LOCATOR_SLOT, PLACE_SLOT],
  // },
];
