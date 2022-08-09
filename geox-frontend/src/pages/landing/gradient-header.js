export const GradientHeader = (props) => {
  const children = props.children;
  const classNames = props.classNames || "";
  return (
    <h1 className={"text-2xl font-bold text-purple-500" + classNames}>
      {children}
    </h1>
  );
};
