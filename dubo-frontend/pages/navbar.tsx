const Navbar = ({ children }: { children: React.ReactNode }) => {
  return (
    <div className="h-16 bg-white w-full border-spBlue border-b">
      <div className="flex flex-row h-full justify-between max-w-5xl m-auto text-spBlue">
        {children}
      </div>
    </div>
  );
};

export default Navbar;
