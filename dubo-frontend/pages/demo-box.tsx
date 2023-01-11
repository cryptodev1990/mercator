import { useEffect, useState } from "react";

const FlickeringCursor = () => {
  const [cursor, setCursor] = useState("|");
  useEffect(() => {
    const interval = setInterval(() => {
      setCursor((c) => (c === "|" ? " " : "|"));
    }, 500);
    return () => clearInterval(interval);
  }, []);

  return <span>{cursor}</span>;
};

const PROMPTS = [
  "What were my sales in Boise yesterday?",
  "Which ZIP codes did the population grow by more than 10% and are economic opportunity zones?",
  "Which candidates passed our phone screen but have not scheduled an on-site?",
];

const SQL = [
  `SELECT city,
     SUM(sales) AS total_sales
   FROM sales
   WHERE date = NOW()::DATE - INTERVAL '1 DAY'
     AND name = 'Boise'
   GROUP BY city`,
  `SELECT 
    zip_code,
    (y1.total_pop - y0.total_pop) / y0.total_pop AS pct_growth
   FROM (
     SELECT
       zip_code,
       total_pop
     FROM acs_5yr_2022
     WHERE opportunity_zone = TRUE
   ) y0
    JOIN (
     SELECT
       zip_code,
       total_pop
     FROM acs_5yr_2022
     WHERE opportunity_zone = TRUE
   ) y1
   ON y0.zip_code = y1.zip_code
   WHERE y1.total_pop > 1000`,
  `SELECT email
   , interview_date
   FROM candidates
   WHERE onsite_date IS NULL`,
];

const RESPONSES = [
  {
    header: ["City", "Sales"],
    data: [["Boise, ID", "$100,000"]],
  },
  {
    header: ["ZIP Code", "Population Growth"],
    data: [["94102", "+0.9%"]],
  },
  {
    header: ["Email", "Interview Date"],
    data: [
      ["andrew@dubo.gg", "2023-03-02"],
      ["rweasley@hogwarts.edu", "2023-01-03"],
      ["dayton@dubo.gg", "2023-01-03"],
    ],
  },
];

const DataFrame = ({ header, data }: { header: string[]; data: any }) => {
  // Format like a pandas dataframe
  return (
    <table className="">
      <thead className="bg-spBlue text-white">
        <tr>
          {header.map((h, i) => (
            <th className="border border-white text-left px-5" key={i}>
              {h}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {data.map((row: any, i: number) => (
          <tr key={i}>
            {row.map((cell: any, j: number) => (
              <td className="border px-5" key={j}>
                {cell}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
};

const DemoBox = () => {
  const [text, setText] = useState("");
  const [revealResponse, setRevealResponse] = useState(false);
  const [index, setIndex] = useState(0);
  const [promptIdx, setPromptIdx] = useState(0);
  const prompt = PROMPTS[promptIdx];
  const response = RESPONSES[promptIdx];

  function resetAndCycle() {
    setText("");
    setRevealResponse(false);
    setIndex(0);
    setPromptIdx((promptIdx + 1) % PROMPTS.length);
  }

  useEffect(() => {
    if (index < prompt.length) {
      const tout = setTimeout(() => {
        setText(text + prompt[index]);
        setIndex(index + 1);
      }, 40);
      return () => clearTimeout(tout);
    } else {
      const tout1 = setTimeout(() => setRevealResponse(true), 1200);
      const tout2 = setTimeout(resetAndCycle, 8000);
      return () => {
        clearTimeout(tout1);
        clearTimeout(tout2);
      };
    }
  }, [index]);

  // After 5 seconds, cycle to the next prompt
  return (
    <>
      <div className="border-b-2 w-[300px] sm:w-[600px]">
        {text}
        <FlickeringCursor />
      </div>
      <div className="h-[10rem]">
        <br />
        {revealResponse && (
          <div className="transition-opacity animate-fadeIn">
            <DataFrame header={response.header} data={response.data} />
          </div>
        )}
      </div>
    </>
  );
};

export default DemoBox;
