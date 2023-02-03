const Legend = ({
  colors,
  text,
  title,
}: {
  colors: number[][];
  text: string[];
  title: string;
}) => {
  return (
    <div className="absolute bottom-0 left-0 z-50 m-2">
      <div className="bg-slate-500 shadow-md text-white p-3">
        <div className="text-sm text-bold">{title}</div>
        <div className="">
          {colors.map((color, i) => {
            return (
              <div key={i} className="flex flex-row justify-start gap-3">
                <div
                  className="h-5 w-5"
                  style={{
                    background: `rgb(${color[0]}, ${color[1]}, ${color[2]})`,
                  }}
                ></div>
                {Number.isFinite(+text[i]) && (
                  <div className="text-sm w-full overflow-hidden">
                    {+text[i]}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default Legend;
