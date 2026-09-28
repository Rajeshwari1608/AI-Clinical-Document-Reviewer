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

      setError("");
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
          <p className="eyebrow">AI / CLINICAL DOCUMENT ANALYSIS</p>

          <h1>AI Clinical Document Reviewer</h1>

          <p className="subtitle">
            Upload or enter a clinical document to generate a
            structured clinical review.
          </p>
        </div>
      </header>

      <main className="main-container">
        <section className="card">
          <div className="section-heading">
            <div>
              <h2>Analyze Clinical Document</h2>

              <p>
                Enter clinical text or upload an image/PDF document.
              </p>
            </div>
          </div>

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

          <div className="or-divider">
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
            <p className="selected-file">
              Selected file: <strong>{selectedFile.name}</strong>
            </p>
          )}

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

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

            <div className="summary-box">
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
                <div className="info-item">
                  <span>Name</span>
                  <strong>
                    {report.patient_info.name || "Not available"}
                  </strong>
                </div>

                <div className="info-item">
                  <span>Age</span>
                  <strong>
                    {report.patient_info.age || "Not available"}
                  </strong>
                </div>

                <div className="info-item">
                  <span>Gender</span>
                  <strong>
                    {report.patient_info.gender || "Not available"}
                  </strong>
                </div>

                <div className="info-item">
                  <span>Date</span>
                  <strong>
                    {report.patient_info.date || "Not available"}
                  </strong>
                </div>
              </div>
            </div>

            <div className="report-section">
              <h3>Symptoms</h3>

              {report.symptoms.length > 0 ? (
                <div className="item-list">
                  {report.symptoms.map((symptom, index) => (
                    <div className="report-item" key={index}>
                      <strong>{symptom.name}</strong>

                      {symptom.details && (
                        <p>{symptom.details}</p>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="muted">
                  No symptoms identified.
                </p>
              )}
            </div>

            <div className="report-section">
              <h3>Diagnoses / Conditions</h3>

              {report.diagnoses.length > 0 ? (
                <div className="item-list">
                  {report.diagnoses.map((diagnosis, index) => (
                    <div className="report-item" key={index}>
                      <strong>{diagnosis.condition}</strong>

                      {diagnosis.details && (
                        <p>{diagnosis.details}</p>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="muted">
                  No diagnoses identified.
                </p>
              )}
            </div>

            <div className="report-section">
              <h3>Medications</h3>

              {report.medications.length > 0 ? (
                <div className="item-list">
                  {report.medications.map((medication, index) => (
                    <div className="report-item" key={index}>
                      <strong>{medication.name}</strong>

                      {medication.dosage && (
                        <p>Dosage: {medication.dosage}</p>
                      )}

                      {medication.frequency && (
                        <p>
                          Frequency: {medication.frequency}
                        </p>
                      )}

                      {medication.details && (
                        <p>{medication.details}</p>
                      )}
                    </div>
                  ))}
                </div>
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
                    <div className="info-item" key={index}>
                      <span>{vital.name}</span>

                      <strong>
                        {vital.value || "Not available"}
                        {vital.unit ? ` ${vital.unit}` : ""}
                      </strong>
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
                <div className="item-list">
                  {report.observations.map(
                    (observation, index) => (
                      <div className="report-item" key={index}>
                        <strong>
                          {observation.observation}
                        </strong>

                        {observation.details && (
                          <p>{observation.details}</p>
                        )}
                      </div>
                    )
                  )}
                </div>
              ) : (
                <p className="muted">
                  No additional observations identified.
                </p>
              )}
            </div>

            <div className="report-section">
              <h3>Concerns</h3>

              {report.concerns.length > 0 ? (
                <div className="item-list">
                  {report.concerns.map((concern, index) => (
                    <div className="report-item" key={index}>
                      <strong>{concern.concern}</strong>

                      {concern.details && (
                        <p>{concern.details}</p>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="muted">
                  No concerns identified.
                </p>
              )}
            </div>

            <div className="report-section">
              <h3>Missing / Incomplete Information</h3>

              {report.missing_information.length > 0 ? (
                <div className="item-list">
                  {report.missing_information.map(
                    (item, index) => (
                      <div className="report-item" key={index}>
                        <strong>{item.field}</strong>

                        {item.details && (
                          <p>{item.details}</p>
                        )}
                      </div>
                    )
                  )}
                </div>
              ) : (
                <p className="muted">
                  No missing information identified.
                </p>
              )}
            </div>

            <div className="report-section">
              <h3>Inconsistencies</h3>

              {report.inconsistencies.length > 0 ? (
                <div className="item-list">
                  {report.inconsistencies.map(
                    (item, index) => (
                      <div className="report-item" key={index}>
                        <strong>{item.issue}</strong>

                        {item.details && (
                          <p>{item.details}</p>
                        )}
                      </div>
                    )
                  )}
                </div>
              ) : (
                <p className="muted">
                  No inconsistencies identified.
                </p>
              )}
            </div>

            <div className="report-section">
              <h3>Review Items</h3>

              {report.review_items.length > 0 ? (
                <div className="item-list">
                  {report.review_items.map((item, index) => (
                    <div className="report-item" key={index}>
                      <strong>{item.item}</strong>

                      {item.details && (
                        <p>{item.details}</p>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="muted">
                  No additional review items identified.
                </p>
              )}
            </div>
          </section>
        )}

        <section className="card history-card">
          <div className="history-header">
            <div>
              <h2>Previous Reports</h2>
            </div>

            <button
              className="small-button"
              onClick={loadHistory}
              disabled={historyLoading}
            >
              {historyLoading ? "Refreshing..." : "Refresh"}
            </button>
          </div>

          {history.length === 0 ? (
            <p className="empty-state">
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
                  <div>
                    <strong>
                      {item.filename ||
                        `${item.source_type} analysis`}
                    </strong>

                    <span>
                      {new Date(
                        item.created_at
                      ).toLocaleString()}
                    </span>

                    {item.summary && (
                      <small>{item.summary}</small>
                    )}
                  </div>

                  <span
                    className={`status ${item.status}`}
                  >
                    {item.status}
                  </span>
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