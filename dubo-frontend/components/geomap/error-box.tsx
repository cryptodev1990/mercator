import { CloseButton } from "../close-button";

const MSG_404 = "Query does not relate to a known data source";

export const ErrorBox = ({
  error,
  onDismiss,
}: {
  error: any;
  onDismiss: any;
}) => {
  let msg;
  if (error.detail === MSG_404) {
    msg = "We couldn't identify data that seemed correct for your search.";
  }
  console.log(error);
  return (
    <div
      className="bg-orange-500 rounded-md shadow-md text-white cursor-pointer"
      onClick={() => onDismiss()}
    >
      <div className="flex flex-col justify-center items-center space-x-2 p-2">
        {/*close button*/}
        <CloseButton
          onClick={() => {
            onDismiss();
          }}
        />
        {msg ?? "Unfortunately, we couldn't process this query"}. Here are some
        suggestions:
        <ul>
          <li>Try rephrasing it.</li>
          <li>Your query may time-out if too resource intensive.</li>
        </ul>
      </div>
    </div>
  );
};
