import { useState } from "react";
import { createClient } from "@supabase/supabase-js";

const supabaseUrl = process.env.REACT_APP_PUBLIC_SUPABASE_URL;
const supabaseAnonKey = process.env.REACT_APP_PUBLIC_SUPABASE_ANON_KEY;

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

const EmailBox = () => {
  const [status, setStatus] = useState("clean");
  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatus("loading");
    const email = e.target[0].value;
    try {
      let ret = await supabase
        .from("waitlist")
        .insert([{ email }], { returning: "minimal" });
      const error = ret.error;

      if (error) {
        console.log(error);
        setStatus("error");
        throw error;
      } else {
        setStatus("resolved");
      }
    } catch (error) {
      setStatus("error");
      alert("Something went wrong. Please try again.");
    }
  };

  if (status === "resolved") {
    return (
      <p className="font-bold text-white">
        We appreciate your interest. We'll contact you shortly.
      </p>
    );
  }

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <div className="flex flex-row bg-white text-slate-600 text-xl w-full gap-3 justify-between items-baseline rounded-2xl">
          <input
            className="focus:outline-none p-3 rounded-l-3xl"
            type="email"
            placeholder="Your email here"
          ></input>
          <button
            className="transition bg-purple-500 text-white cursor-pointer 2 p-3 pr-3 hover:bg-tertiary rounded-r-2xl font-bold overflow-x-clip whitespace-nowrap text-ellipsis"
            disabled={status === "loading"}
          >
            {status === "loading" ? "Submitting..." : "Get early access"}
          </button>
        </div>
      </div>
    </form>
  );
};

export { EmailBox };
