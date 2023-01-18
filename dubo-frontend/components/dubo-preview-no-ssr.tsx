import dynamic from "next/dynamic";

const DuboPreview = dynamic(() => import("./dubo-preview"), {
  ssr: false,
});

export default DuboPreview;
