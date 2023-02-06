import dynamic from "next/dynamic";

const Census = dynamic(() => import("../../components/geomap/geomap"), {
  ssr: false,
});

export default Census;
