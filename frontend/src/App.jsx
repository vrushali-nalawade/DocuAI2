import { useState } from "react";
import UploadForm from "./components/UploadForm";
import ResultCard from "./components/ResultCard";
import "./App.css";

function App() {
  const [result, setResult] = useState(null);

  return (
    <div className="app-container">
      <div className="app-shell">
        <section className="hero">
          <h1>Document AI</h1>
          <p>Upload PDF, DOCX, JPG, PNG, WEBP</p>
        </section>

        <section className="panel">
          <UploadForm setResult={setResult} />
        </section>

        {result && (
          <section className="panel">
            <ResultCard result={result} />
          </section>
        )}
      </div>
    </div>
  );
}

export default App;