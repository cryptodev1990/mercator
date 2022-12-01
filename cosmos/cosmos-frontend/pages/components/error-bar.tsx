import { useSelector } from "react-redux";
import { selectSearchState } from "src/search/search-slice";
import { useOsmQueryGetQuery } from "src/store/search-api";
import AnnouncementBar from "./announcement-bar";

function getMessageFromError(error: any) {
  if (error?.status === 422) {
    // TODO suggestions here would be nice
    return `We don't support this kind of question at this time. Please try a different query.`;
  }
  return "Something went wrong. Please try again.";
}

const ErrorBar = () => {
  const { inputText } = useSelector(selectSearchState);

  const { data, error } = useOsmQueryGetQuery(
    {
      query: inputText || "",
    },
    {
      skip: inputText?.length === 0 ?? true,
    }
  );

  if (!error) {
    return null;
  }

  const message = getMessageFromError(error);
  return <AnnouncementBar markdown={message} type="error" />;
};

export default ErrorBar;
