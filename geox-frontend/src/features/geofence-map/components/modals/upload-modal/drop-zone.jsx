import { CancelIcon } from "../../../../../common/components/icons";
import Loading from "react-loading";

function convertBytesToHumanReadable(bytes) {
  const sizes = ["Bytes", "KB", "MB", "GB", "TB"];
  if (bytes === 0) {
    return "0 Bytes";
  }
  const i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)), 10);
  if (i === 0) {
    return `${bytes} ${sizes[i]})`;
  }
  return `${(bytes / 1024 ** i).toFixed(1)} ${sizes[i]}`;
}

export function DropZone({
  getInputProps,
  getRootProps,
  files,
  setFiles,
  loading,
}) {
  const acceptedFilesList = files.map((file) => (
    <li key={file.path} className="flex flex-row space-x-1">
      {file.path} - {convertBytesToHumanReadable(file.size)}
      <button onClick={() => removeFile(file)}>
        <CancelIcon className="hover:fill-red-400" />
      </button>
      <div>
        {loading && <Loading type="spin" color="#000" height={20} width={20} />}
      </div>
    </li>
  ));

  function removeFile(file) {
    setFiles(files.filter((f) => f !== file));
  }

  if (files.length > 0) {
    return (
      <aside>
        <h4>File detected:</h4>
        <ul>{acceptedFilesList}</ul>
      </aside>
    );
  }

  return (
    <section className="relative w-full border border-dotted border-black space-x-3 my-5 text-black text-center h-[100px]">
      <div
        {...getRootProps({ className: "dropzone" })}
        className="flex items-center align-center justify-center h-full w-full cursor-pointer"
      >
        <input {...getInputProps()} />
        <p>Drag file or click here to upload</p>
      </div>
    </section>
  );
}
