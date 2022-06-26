import React from 'react';
import logo from './logo.svg';
import { Counter } from './features/counter/Counter';
import './App.css';

function App() {
  const [message, setMessage] = React.useState<String>("");
  React.useEffect(() => {
    const url = String(process.env.REACT_APP_BACKEND_URL);
    fetch(url, {
         headers: {
           'Accept': 'application/json'
         }})
        .then(x => {
	    console.log(x);
            return x.json()
	})
        .then(x => {
            setMessage(JSON.stringify(x))
	})
  }, []);
  const lilapp = (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <Counter />
        <p>
          Edit <code>src/App.tsx</code> and save to reload.
        </p>
        <span>
          <span>Learn </span>
          <a
            className="App-link"
            href="https://reactjs.org/"
            target="_blank"
            rel="noopener noreferrer"
          >
            React
          </a>
          <span>, </span>
          <a
            className="App-link"
            href="https://redux.js.org/"
            target="_blank"
            rel="noopener noreferrer"
          >
            Redux
          </a>
          <span>, </span>
          <a
            className="App-link"
            href="https://redux-toolkit.js.org/"
            target="_blank"
            rel="noopener noreferrer"
          >
            Redux Toolkit
          </a>
          ,<span> and </span>
          <a
            className="App-link"
            href="https://react-redux.js.org/"
            target="_blank"
            rel="noopener noreferrer"
          >
            React Redux
          </a>
        </span>
        {message}
      </header>
    </div>
  );
  return <div>We just got this domain. We'll have something interesting here soon.</div>
}

export default App;
