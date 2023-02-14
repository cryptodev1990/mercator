export const TrackedText = ({ text }: { text: string }) => {
  return (
    <div className="relative tracking-tighter">
      <h1 className="text-2xl font-black font-outline-4 z-0">{text}</h1>
      <span className="text-2xl absolute top-0 left-0 z-30 text-slate-900">
        {text}
      </span>
    </div>
  );
};
