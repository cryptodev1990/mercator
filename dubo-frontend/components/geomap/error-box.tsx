import React from "react";

import { CloseButton } from "../close-button";

const MSG_404 = "Query does not relate to a known data source";

export const ErrorBox = ({
  showErrorBox,
  setShowErrorBox,
  error,
  onDismiss,
}: {
  showErrorBox: any;
  setShowErrorBox: any;
  error: any;
  onDismiss: any;
}) => {
  let msg;
  if (error.detail === MSG_404) {
    msg = "We couldn't identify data that seemed correct for your search.";
  }
  // console.log(error);
  return (
    <>
      {showErrorBox ? (
        <div
          className="bg-[#342978] rounded-md shadow-2xl text-white hover:cursor-pointer z-20 sm:w-2/3 w-full animate-wiggle"
        >
          <div className="flex justify-end">
            {/*close button*/}
            <CloseButton
              onClick={() => {
                onDismiss();
              }}
            />
          </div>

          <div className="flex flex-col justify-center items-start space-x-2 py-2 px-5">
            {msg ?? "Unfortunately, we couldn't process this query"}. Here are
            some suggestions:
            <ul>
              <li>Try rephrasing it.</li>
              <li>Your query may time-out if too resource intensive.</li>
            </ul>
          </div>
        </div>
      ) : null}
    </>
  );
};
