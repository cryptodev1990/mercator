import { MdCancel } from "react-icons/md";
import Loading from "react-loading";

export function DropZone({
  getInputProps,
  getRootProps,
  files,
  setFiles,
  loading,
}) {
  const acceptedFilesList = files.map((file) => (
    <li key={file.path} className="flex flex-row space-x-1 cursor-pointer">
      {file.path} - {file.size} bytes
      <button onClick={() => removeFile(file)}>
        <MdCancel className="hover:fill-red-400" />
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
        {...getRootProps({ className: "dropzone m-auto flex justify-center" })}
      >
        <input {...getInputProps()} />
        <p>Drag file here, or click to select a file</p>
      </div>
    </section>
  );
}
