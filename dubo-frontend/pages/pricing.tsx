import EmailBox from "../lib/email-box";
import Navbar from "../lib/navbar";
import Section from "../lib/section";

const Pricing = () => {
  return (
    <>
      <Navbar />
      <Section size="full">
        <div className="flex flex-col items-center justify-center h-full">
          <br />
          <h1 className="text-3xl font-bold">Pricing</h1>
          <br />
          <p className="w-[50%]">
            Interested in using dubo? We are currently in a closed beta but are
            accepting a limited number of users. Please fill out the form below
            for a demo.
          </p>
          <div></div>
          <br />
        </div>
        <EmailBox autoFocus />
      </Section>
    </>
  );
};

export default Pricing;