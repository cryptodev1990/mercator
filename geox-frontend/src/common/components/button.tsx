export const Button = (props: any) => {
  const { children, ...rest } = props;
  return (
    <button
      {...rest}
      className="inline-flex items-center py-2 px-3 text-sm font-medium text-center text-white bg-blue-700 rounded-lg hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800"
    >
      {props.children}
    </button>
  );
};

export const FlashButton = (props: any) => {
  const { children, ...rest } = props;
  return (
    <button
      {...rest}
      className="text-base sm:text-sm px-6 button lg:button-sm bg-ublue hover:bg-violet-600 text-white font-bold transition-all p-2 rounded"
    >
      {props.children}
    </button>
  );
};

export default function GenericButton(props: any) {
  const { text, ...rest } = props;
  return (
    <>
      <button
        type="button"
        {...rest}
        className={`inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 ${props.extraClasses}`}
      >
        {text}
      </button>
    </>
  );
}
