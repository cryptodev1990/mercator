const FAQ = () => (
  <div className="flex w-full justify-center">
    <div className="flex flex-col items-center justify-center max-w-2xl">
      <div className="flex flex-col items-start justify-center w-full h-full m-3 p-3">
        <h1 className="text-2xl">About dubo</h1>
        <div className="flex flex-col items-center justify-center max-w-5xl h-full">
          <div>
            <strong>How does dubo work?</strong>
            <p>
              dubo relies on GPTs trained on SQL to be able to do data
              aggregations.
            </p>
            <strong>Is this preferable to writing SQL?</strong>
            <p>
              Often but not always. For very complex queries, dubo cannot
              replicate the specifics or important behavior.
            </p>
            <strong>Is this a commercial product?</strong>
            <p>
              Yes, but we offer a free tier for personal and commercial use. We
              are currently in a closed beta but are accepting a limited number
              of users, which you can sign up for by contacting
              founders@dubo.gg.
            </p>
            <strong>What data do you store?</strong>
            <p>
              We store the queries our users run, the emitted SQL from our
              models, and any schema or data descriptions that are sent to us.
              We do not store any data content itself.
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
);

export default FAQ;
