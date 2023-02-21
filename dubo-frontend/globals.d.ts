type DataFrame = {
  columns: string[];
  data: any[];
};

type DatabaseSchema = "polygon-blocks" | "bitcoin-blocks" | "ethereum-blocks";

type SampleDataKey = "census" | "fortune500";

type MetaCensusRecord = {
  name: string;
  dubo_name: string;
  label: string;
  concept: string | null;
};

type DataSample = {
  data_header: any[];
  data_sample: any[][];
};
