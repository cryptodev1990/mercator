import { GradientHeader } from "./gradient-header";

export const ProductSection = ({ header, copytext, align, video }) => {
  return (
    <section
      className={`mx-auto max-w-5xl my-10 flex gap-10`}
      style={{ flexDirection: "left" === align ? "row-reverse" : "row" }}
    >
      <div className="flex flex-col w-[25%]">
        <GradientHeader>{header}</GradientHeader>
        <p className="text-base text-white text-left">{copytext}</p>
      </div>
      <div
        style={{
          background: "#000",
          overflow: "hidden",
          position: "relative",
          aspectRatio: "16/9",
          width: "100%",
          borderRadius: "5px",
        }}
      >
        <iframe
          style={{
            width: "300%",
            border: "none",
            height: "100%",
            marginLeft: "-100%",
          }}
          src={`https://www.youtube.com/embed/${video}?controls=0&modestbranding=1&showinfo=0&rel=0&autoplay=1&loop=1&mute=1&playlist=${video}`}
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          title={header}
          frameBorder="0"
        ></iframe>
      </div>
    </section>
  );
};
