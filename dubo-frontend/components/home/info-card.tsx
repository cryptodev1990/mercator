const InfoCard = ({
  header,
  children,
}: {
  header: string;
  children: React.ReactNode;
}) => {
  return (
    <div className="flex flex-col items-baseline justify-start">
      <h1 className="text-xl font-bold text-spBlue">{header}</h1>
      <div className="text-md leading-none">{children}</div>
    </div>
  );
};

export default InfoCard;
