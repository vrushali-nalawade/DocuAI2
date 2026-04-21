import { useRef, useState } from "react";
import { analyzeDocument } from "../api";

function UploadForm({ setResult }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const fileInputRef = useRef(null);

  const getFileType = (filename) => {
    const ext = filename.split(".").pop().toLowerCase();
    if (ext === "pdf") return "pdf";
    if (ext === "docx") return "docx";
    if (["png", "jpg", "jpeg", "webp"].includes(ext)) return ext;
    return null;
  };

  const convertToBase64 = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);

      reader.onload = () => {
        const result = reader.result;
        if (!result) {
          reject(new Error("Failed to read file."));
          return;
        }

        const base64String = result.split(",")[1];
        resolve(base64String);
      };

      reader.onerror = (error) => reject(error);
    });
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files?.[0];
    setError("");
    setResult(null);

    if (!selectedFile) return;

    const fileType = getFileType(selectedFile.name);

    if (!fileType) {
      setFile(null);
      setError("Unsupported file type. Please upload PDF, DOCX, JPG, JPEG, PNG, or WEBP.");
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
      return;
    }

    setFile(selectedFile);
  };

  const handleRemoveFile = () => {
    setFile(null);
    setError("");
    setResult(null);
    setLoading(false);

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setResult(null);

    if (!file) {
      setError("Please upload a file first.");
      return;
    }

    const fileType = getFileType(file.name);

    if (!fileType) {
      setError("Unsupported file type. Please upload PDF, DOCX, JPG, JPEG, PNG, or WEBP.");
      return;
    }

    try {
      setLoading(true);

      const fileBase64 = await convertToBase64(file);

      const payload = {
        fileName: file.name,
        fileType,
        fileBase64,
      };

      const response = await analyzeDocument(payload);
      setResult(response);
    } catch (err) {
      console.error(err);

      const backendMessage =
        err?.response?.data?.detail ||
        err?.response?.data?.message ||
        "Something went wrong while analyzing the document.";

      setError(backendMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form className="upload-form" onSubmit={handleSubmit}>
      <div className="upload-header">
        <h2>Upload Document</h2>
        <p>Supported formats: PDF, DOCX, PNG, JPG, JPEG, WEBP</p>
      </div>

      <label className="dropzone">
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx,.png,.jpg,.jpeg,.webp"
          onChange={handleFileChange}
        />
        <div className="dropzone-content">
          <div className="upload-icon">⬆</div>
          <h3>Drag & drop or click to upload</h3>
          <p>Files are converted to Base64 before API submission</p>
        </div>
      </label>

      {file && (
        <div className="file-info">
          <div className="file-left">
            <span className="chip">Selected File</span>
            <p className="file-name">{file.name}</p>
          </div>

          <div className="file-actions">
            <div className="file-meta">
              <span>{(file.size / 1024).toFixed(2)} KB</span>
              <span>{getFileType(file.name)?.toUpperCase()}</span>
            </div>

            <button
              type="button"
              className="remove-file-btn"
              onClick={handleRemoveFile}
              aria-label="Remove selected file"
              title="Remove file"
            >
              ✕
            </button>
          </div>
        </div>
      )}

      <button type="submit" disabled={loading}>
        {loading ? "Analyzing..." : "Analyze Document"}
      </button>

      {error && <p className="error">{error}</p>}
    </form>
  );
}

export default UploadForm;