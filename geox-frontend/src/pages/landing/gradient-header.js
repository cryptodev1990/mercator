export const GradientHeader = (props) => {
  const children = props.children;
  const classNames = props.classNames || "";
  return (
    <h1
      className={
        "text-2xl font-extrabold text-transparent bg-clip-text bg-gradient-to-br from-white to-blue-500 " +
        classNames
      }
    >
      {children}
    </h1>
  );
};
