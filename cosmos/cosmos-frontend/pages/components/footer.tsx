const Footer = () => {
  return (
    <footer className="fixed bottom-0 p-3 text-sm bg-[#121212] w-full text-center">
      <span className="p-1">Powered by</span>
      <span className="p-1">
        <a href="https://mercator.tech">Mercator</a>
      </span>
      <span className="p-1">•</span>
      <span className="p-1">
        <a href="https://openstreetmap.org">OpenStreetMap</a>
      </span>
      <span className="p-1">•</span>
      <span className="p-1">
        <a href="https://vis.gl">Vis.gl</a>
      </span>
      <br />
    </footer>
  );
};

export default Footer;
