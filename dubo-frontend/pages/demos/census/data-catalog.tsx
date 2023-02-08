import {
  DataCatalogContent,
  MetaCensusRecord,
} from "../../../components/geomap/data-catalog-content";

const BACKEND_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL || "http://dubo-api.mercator.tech";
const ENDPOINT = `${BACKEND_URL}/demo/census/variables`;

const DataCatalogPage = ({ data }: { data: MetaCensusRecord[] }) => {
  return <DataCatalogContent ssrData={data} />;
};

// fetch the data and then render the component
export async function getStaticProps() {
  const data = await fetch(ENDPOINT).then((res) => res.json());
  return { props: { data } };
}

export default DataCatalogPage;
