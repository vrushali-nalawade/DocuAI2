function ResultCard({ result }) {
  const { fileName, summary, entities, sentiment } = result;

  const getSentimentClass = (sentiment) => {
    if (!sentiment) return "neutral";
    const value = sentiment.toLowerCase();
    if (value === "positive") return "positive";
    if (value === "negative") return "negative";
    return "neutral";
  };

  return (
    <div className="result-card">
      <div className="result-top">
        <div>
          <h2>Analysis Result</h2>
          <p className="muted">{fileName}</p>
        </div>

        <span className={`sentiment-badge ${getSentimentClass(sentiment)}`}>
          {sentiment}
        </span>
      </div>

      <div className="result-section">
        <h3>Summary</h3>
        <p>{summary}</p>
      </div>

      <div className="result-section">
        <h3>Extracted Entities</h3>
        <div className="entity-grid">
          <div className="entity-box">
            <strong>Names</strong>
            <p>{entities?.names?.join(", ") || "None"}</p>
          </div>

          <div className="entity-box">
            <strong>Dates</strong>
            <p>{entities?.dates?.join(", ") || "None"}</p>
          </div>

          <div className="entity-box">
            <strong>Organizations</strong>
            <p>{entities?.organizations?.join(", ") || "None"}</p>
          </div>

          <div className="entity-box">
            <strong>Amounts</strong>
            <p>{entities?.amounts?.join(", ") || "None"}</p>
          </div>
        </div>
      </div>

      <div className="result-section">
        <h3>API Response Shape</h3>
        <pre className="json-preview">
{JSON.stringify(result, null, 2)}
        </pre>
      </div>
    </div>
  );
}

export default ResultCard;