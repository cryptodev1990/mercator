import React from 'react';
import * as ReactDOM from 'react-dom/client';
import { HomePage } from './pages';

function App() {
  return <HomePage />;
}

ReactDOM.createRoot(document.getElementById('react-container')).render(<App />);
