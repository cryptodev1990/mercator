const Section = ({ children }: { children: React.ReactNode; size: string }) => {
  return (
    <div className="flex flex-col items-center justify-center w-full h-[50%]">
      {children}
    </div>
  );
};

export default Section;