import { GradientHeader } from "./gradient-header";

export const ProductSection = ({ header, copytext, align, video }) => {
  return (
    <section className={`mx-auto max-w-5xl my-10 snap-start`}>
      <div className="sm:hidden display sm:top-0 sm:left-0 bg-ublue w-full bg-opacity-95 p-5">
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
        <div className="sm:block sm:absolute hidden top-0 left-0 bg-ublue w-full bg-opacity-95 p-5">
          <GradientHeader>{header}</GradientHeader>
          <p className="text-base text-white text-left">{copytext}</p>
        </div>

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
