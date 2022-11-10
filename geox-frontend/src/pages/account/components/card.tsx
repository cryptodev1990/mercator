export const Card = ({
  children,
  className,
  title,
}: {
  children: React.ReactNode;
  className?: string;
  title?: string;
}): JSX.Element => {
  return (
    <div className={`card bg-slate-100 pt-4 text-[#2d2d2d] ${className}`}>
      {title && <h2 className="card-title px-7 translate-y-3">{title}</h2>}
      <div className="card-body">{children}</div>
    </div>
  );
};
