import { useEffect, useState } from "react";
import axios from "axios";
import "./App.css";

const API_BASE_URL = "http://127.0.0.1:8000";

type Report = {
  report_summary: string;
  primary_concerns: string[];
  patient_info: {
    name?: string | null;
    age?: string | null;
    gender?: string | null;
    date?: string | null;
  };
  symptoms: {
    name: string;
    details?: string | null;
  }[];
  diagnoses: {
    condition: string;
    details?: string | null;
  }[];
  medications: {
    name: string;
    dosage?: string | null;
    frequency?: string | null;
    details?: string | null;
  }[];
  vitals: {
    name: string;
    value?: string | null;
    unit?: string | null;
  }[];
  allergies: string[];
  observations: {
    observation: string;
    details?: string | null;
  }[];
  concerns: {
    concern: string;
    details?: string | null;
  }[];
  missing_information: {
    field: string;
    details?: string | null;
  }[];
  inconsistencies: {
    issue: string;
    details?: string | null;
  }[];
  review_items: {
    item: string;
    details?: string | null;
  }[];
};

type HistoryItem = {
  analysis_id: number;
  source_type: string;
  filename?: string | null;
  status: string;
  summary?: string | null;
  created_at: string;
  error_message?: string | null;
};

function App() {
  const [text, setText] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [report, setReport] = useState<Report | null>(null);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [error, setError] = useState("");

  const loadHistory = async () => {
    try {
      setHistoryLoading(true);

      const response = await axios.get(
        `${API_BASE_URL}/api/analyze/history`
      );

      setHistory(response.data.reports ?? []);
    } catch (requestError: unknown) {
      console.error("History request failed:", requestError);
      setError("Unable to load previous reports.");
    } finally {
      setHistoryLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const handleFileChange = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = event.target.files?.[0] ?? null;

    setSelectedFile(file);
    setError("");
    setReport(null);

    if (file) {
      setText("");
    }
  };

  const handleAnalyze = async () => {
    setError("");
    setReport(null);

    if (!text.trim() && !selectedFile) {
      setError(
        "Please enter clinical text or upload an image/PDF."
      );
      return;
    }

    try {
      setLoading(true);

      if (text.trim()) {
        const result = await axios.post(
          `${API_BASE_URL}/api/analyze/text`,
          {
            text: text.trim(),
          }
        );

        setReport(result.data.report);
      } else if (selectedFile) {
        const formData = new FormData();
        formData.append("file", selectedFile);

        const fileName = selectedFile.name.toLowerCase();

        if (
          fileName.endsWith(".png") ||
          fileName.endsWith(".jpg") ||
          fileName.endsWith(".jpeg") ||
          fileName.endsWith(".bmp") ||
          fileName.endsWith(".tif") ||
          fileName.endsWith(".tiff")
        ) {
          const result = await axios.post(
            `${API_BASE_URL}/api/analyze/image`,
            formData
          );

          setReport(result.data.report);
        } else if (fileName.endsWith(".pdf")) {
          const result = await axios.post(
            `${API_BASE_URL}/api/analyze/pdf`,
            formData
          );

          setReport(result.data.report);
        } else {
          setError(
            "Unsupported file type. Please upload an image or PDF."
          );
          return;
        }
      }

      await loadHistory();
    } catch (requestError: unknown) {
      if (axios.isAxiosError(requestError)) {
        const detail = requestError.response?.data?.detail;

        if (typeof detail === "string") {
          setError(detail);
        } else {
          setError(
            "Unable to analyze the document. Please try again."
          );
        }
      } else {
        setError(
          "Unable to analyze the document. Please try again."
        );
      }
    } finally {
      setLoading(false);
    }
  };

  const openPreviousReport = async (analysisId: number) => {
    try {
      setError("");
      setLoading(true);

      const response = await axios.get(
        `${API_BASE_URL}/api/analyze/history/${analysisId}`
      );

      if (response.data.report) {
        setReport(response.data.report);
      } else {
        setError(
          response.data.error_message ||
            "This analysis does not contain a report."
        );
      }
    } catch (requestError: unknown) {
      if (axios.isAxiosError(requestError)) {
        const detail = requestError.response?.data?.detail;

        if (typeof detail === "string") {
          setError(detail);
        } else {
          setError("Unable to open the selected report.");
        }
      } else {
        setError("Unable to open the selected report.");
      }
    } finally {
      setLoading(false);
    }
  };

  const clearForm = () => {
    setText("");
    setSelectedFile(null);
    setReport(null);
    setError("");

    const fileInput = document.getElementById(
      "file-upload"
    ) as HTMLInputElement | null;

    if (fileInput) {
      fileInput.value = "";
    }
  };

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>AI Clinical Document Reviewer</h1>
          <p>
            Upload or enter a clinical document to generate a
            structured clinical review.
          </p>
        </div>
      </header>

      <main className="container">
        <section className="card">
          <h2>Analyze Clinical Document</h2>

          <label htmlFor="clinical-text">
            Clinical text
          </label>

          <textarea
            id="clinical-text"
            value={text}
            onChange={(event) => {
              setText(event.target.value);
              setSelectedFile(null);
              setReport(null);
              setError("");
            }}
            placeholder="Paste clinical notes, symptoms, medications, vitals, or other clinical information here..."
            rows={10}
          />

          <div className="divider">
            <span>OR</span>
          </div>

          <label htmlFor="file-upload">
            Upload document
          </label>

          <input
            id="file-upload"
            type="file"
            accept=".png,.jpg,.jpeg,.bmp,.tif,.tiff,.pdf"
            onChange={handleFileChange}
          />

          {selectedFile && (
            <p className="file-name">
              Selected file: <strong>{selectedFile.name}</strong>
            </p>
          )}

          {error && <div className="error">{error}</div>}

          <div className="button-row">
            <button
              className="primary-button"
              onClick={handleAnalyze}
              disabled={loading}
            >
              {loading ? "Analyzing..." : "Analyze Document"}
            </button>

            <button
              className="secondary-button"
              onClick={clearForm}
              disabled={loading}
            >
              Clear
            </button>
          </div>
        </section>

        {report && (
          <section className="card report-card">
            <h2>Clinical Review Report</h2>

            <div className="report-section summary-section">
              <h3>Report Summary</h3>
              <p>{report.report_summary}</p>
            </div>

            <div className="report-section">
              <h3>Primary Concerns</h3>

              {report.primary_concerns.length > 0 ? (
                <ul>
                  {report.primary_concerns.map((concern, index) => (
                    <li key={index}>{concern}</li>
                  ))}
                </ul>
              ) : (
                <p className="muted">
                  No primary concerns identified.
                </p>
              )}
            </div>

            <div className="report-section">
              <h3>Patient Information</h3>

              <div className="info-grid">
                <div>
                  <strong>Name</strong>
                  <span>
                    {report.patient_info.name || "Not available"}
                  </span>
                </div>

                <div>
                  <strong>Age</strong>
                  <span>
                    {report.patient_info.age || "Not available"}
                  </span>
                </div>

                <div>
                  <strong>Gender</strong>
                  <span>
                    {report.patient_info.gender || "Not available"}
                  </span>
                </div>

                <div>
                  <strong>Date</strong>
                  <span>
                    {report.patient_info.date || "Not available"}
                  </span>
                </div>
              </div>
            </div>

            <div className="report-section">
              <h3>Symptoms</h3>

              {report.symptoms.length > 0 ? (
                <ul>
                  {report.symptoms.map((symptom, index) => (
                    <li key={index}>
                      <strong>{symptom.name}</strong>
                      {symptom.details &&
                        ` — ${symptom.details}`}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="muted">
                  No symptoms identified.
                </p>
              )}
            </div>

            <div className="report-section">
              <h3>Diagnoses / Conditions</h3>

              {report.diagnoses.length > 0 ? (
                <ul>
                  {report.diagnoses.map((diagnosis, index) => (
                    <li key={index}>
                      <strong>{diagnosis.condition}</strong>
                      {diagnosis.details &&
                        ` — ${diagnosis.details}`}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="muted">
                  No diagnoses identified.
                </p>
              )}
            </div>

            <div className="report-section">
              <h3>Medications</h3>

              {report.medications.length > 0 ? (
                <ul>
                  {report.medications.map((medication, index) => (
                    <li key={index}>
                      <strong>{medication.name}</strong>
                      {medication.dosage &&
                        ` — ${medication.dosage}`}
                      {medication.frequency &&
                        `, ${medication.frequency}`}
                      {medication.details &&
                        ` — ${medication.details}`}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="muted">
                  No medications identified.
                </p>
              )}
            </div>

            <div className="report-section">
              <h3>Vitals</h3>

              {report.vitals.length > 0 ? (
                <div className="info-grid">
                  {report.vitals.map((vital, index) => (
                    <div key={index}>
                      <strong>{vital.name}</strong>
                      <span>
                        {vital.value || "Not available"}
                        {vital.unit ? ` ${vital.unit}` : ""}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="muted">
                  No vitals identified.
                </p>
              )}
            </div>

            <div className="report-section">
              <h3>Allergies</h3>

              {report.allergies.length > 0 ? (
                <ul>
                  {report.allergies.map((allergy, index) => (
                    <li key={index}>{allergy}</li>
                  ))}
                </ul>
              ) : (
                <p className="muted">
                  No allergy information identified.
                </p>
              )}
            </div>

            <div className="report-section">
              <h3>Observations</h3>

              {report.observations.length > 0 ? (
                <ul>
                  {report.observations.map(
                    (observation, index) => (
                      <li key={index}>
                        <strong>
                          {observation.observation}
                        </strong>
                        {observation.details &&
                          ` — ${observation.details}`}
                      </li>
                    )
                  )}
                </ul>
              ) : (
                <p className="muted">
                  No additional observations identified.
                </p>
              )}
            </div>

            <div className="report-section">
              <h3>Concerns</h3>

              {report.concerns.length > 0 ? (
                <ul>
                  {report.concerns.map((concern, index) => (
                    <li key={index}>
                      <strong>{concern.concern}</strong>
                      {concern.details &&
                        ` — ${concern.details}`}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="muted">
                  No concerns identified.
                </p>
              )}
            </div>

            <div className="report-section">
              <h3>Missing / Incomplete Information</h3>

              {report.missing_information.length > 0 ? (
                <ul>
                  {report.missing_information.map(
                    (item, index) => (
                      <li key={index}>
                        <strong>{item.field}</strong>
                        {item.details &&
                          ` — ${item.details}`}
                      </li>
                    )
                  )}
                </ul>
              ) : (
                <p className="muted">
                  No missing information identified.
                </p>
              )}
            </div>

            <div className="report-section">
              <h3>Inconsistencies</h3>

              {report.inconsistencies.length > 0 ? (
                <ul>
                  {report.inconsistencies.map(
                    (item, index) => (
                      <li key={index}>
                        <strong>{item.issue}</strong>
                        {item.details &&
                          ` — ${item.details}`}
                      </li>
                    )
                  )}
                </ul>
              ) : (
                <p className="muted">
                  No inconsistencies identified.
                </p>
              )}
            </div>

            <div className="report-section">
              <h3>Review Items</h3>

              {report.review_items.length > 0 ? (
                <ul>
                  {report.review_items.map((item, index) => (
                    <li key={index}>
                      <strong>{item.item}</strong>
                      {item.details &&
                        ` — ${item.details}`}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="muted">
                  No additional review items identified.
                </p>
              )}
            </div>
          </section>
        )}

        <section className="card">
          <div className="section-header">
            <h2>Previous Reports</h2>

            <button
              className="small-button"
              onClick={loadHistory}
              disabled={historyLoading}
            >
              {historyLoading ? "Refreshing..." : "Refresh"}
            </button>
          </div>

          {history.length === 0 ? (
            <p className="muted">
              No previous analyses available.
            </p>
          ) : (
            <div className="history-list">
              {history.map((item) => (
                <button
                  key={item.analysis_id}
                  className="history-item"
                  onClick={() =>
                    openPreviousReport(item.analysis_id)
                  }
                >
                  <div className="history-main">
                    <strong>
                      {item.filename ||
                        `${item.source_type} analysis`}
                    </strong>

                    <span>
                      {new Date(
                        item.created_at
                      ).toLocaleString()}
                    </span>
                  </div>

                  <div className="history-meta">
                    <span
                      className={`status ${item.status}`}
                    >
                      {item.status}
                    </span>

                    {item.summary && (
                      <span className="history-summary">
                        {item.summary}
                      </span>
                    )}
                  </div>
                </button>
              ))}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;