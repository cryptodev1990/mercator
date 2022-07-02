import * as ReactDOM from 'react-dom/client';
import { HomePage, NotebookPage } from './pages';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

function RoutesIndex() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/notebook" element={<NotebookPage />} />
      </Routes>
    </BrowserRouter>
  );
}

function App() {
  return <RoutesIndex />;
}

ReactDOM.createRoot(document.getElementById('react-container')).render(<App />);
