import { createContext } from "react";
import { Namespace } from "../../../../../../client";

export const NamespaceContext = createContext<Namespace | null>(null);
