const nab = (arr: string[]) => arr[Math.floor(Math.random() * arr.length)];

const SUGGESTIONS = [
  "All the coffee shops in California",
  "Where does it rain fewer than six days out of the year?",
  "Where is the tallest mountain in California?",
  "What's a location that's within 100 miles of San Francisco and within 5 minutes of a freeway?",
  "Where can I go that has a population of 100,000 or more and is within 100 miles of San Francisco?",
  "What EV charging stations are on the route from San Francisco to Los Angeles?",
];

const Tag = ({
  text,
  onClick,
}: {
  text: string;
  onClick: (text: string) => void;
}) => (
  <div
    className={
      `rounded-full px-5 py-3 text-sm text-center font-semibold text-slate-200 mr-2 mb-2 cursor-pointer z-10 ` +
      nab(["bg-blue-500", "bg-red-600", "bg-purple-700", "bg-orange-600"])
    }
    onClick={() => {
      onClick(text);
    }}
  >
    <p>{text}</p>
  </div>
);

const SearchSuggestions = () => {
  const tags = SUGGESTIONS.map((suggestion, i) => (
    <Tag key={i} text={suggestion} onClick={(text) => console.log(text)} />
  ));
  return (
    <div>
      <div className="flex flex-col justify-center items-start">
        <div className="my-5">
          <span>Some suggestions</span>
        </div>
        {tags}
      </div>
    </div>
  );
};

export default SearchSuggestions;
