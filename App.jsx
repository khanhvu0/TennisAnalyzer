import React, { useState } from "react";
import axios from "axios";

function App() {
  const [userFile, setUserFile] = useState(null);
  const [proFile, setProFile] = useState(null);
  const [userKeyEvents, setUserKeyEvents] = useState({
    ballRelease: "",
    trophyPosition: "",
    racquetLowPoint: "",
    impact: "",
  });
  const [proKeyEvents, setProKeyEvents] = useState({
    ballRelease: "",
    trophyPosition: "",
    racquetLowPoint: "",
    impact: "",
  });
  const [analysisResult, setAnalysisResult] = useState(null);
  const [selectedKeyEvent, setSelectedKeyEvent] = useState("");

  const handleFileChange = (e, setFile) => {
    setFile(e.target.files[0]);
  };

  const handleKeyEventsChange = (e, setKeyEvents) => {
    const { name, value } = e.target;
    setKeyEvents((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!userFile || !proFile) {
      alert("Please upload both user and pro files.");
      return;
    }

    if (!selectedKeyEvent) {
      alert("Please select a key event to analyze.");
      return;
    }

    try {
      const formData = new FormData();
      formData.append("user", userFile);
      formData.append("pro", proFile);

      const keyEvents = JSON.stringify([
        {
          ball_release: parseFloat(userKeyEvents.ballRelease),
          trophy_position: parseFloat(userKeyEvents.trophyPosition),
          racquet_low_point: parseFloat(userKeyEvents.racquetLowPoint),
          impact: parseFloat(userKeyEvents.impact),
        },
        {
          ball_release: parseFloat(proKeyEvents.ballRelease),
          trophy_position: parseFloat(proKeyEvents.trophyPosition),
          racquet_low_point: parseFloat(proKeyEvents.racquetLowPoint),
          impact: parseFloat(proKeyEvents.impact),
        },
      ]);

      formData.append("key_events", keyEvents);
      formData.append("selected_key_event", selectedKeyEvent);

      const response = await axios.post("http://127.0.0.1:5004/analyze", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      setAnalysisResult(response.data.result);
      console.log(response.data);
    } catch (error) {
      console.error("Error:", error);
      alert("An error occurred during analysis.");
    }
  };

  return (
    <div style={{ padding: "20px", fontFamily: "Arial, sans-serif" }}>
      <h1>Tennis Serve Analyzer</h1>
      <form onSubmit={handleSubmit}>
        <div>
          <label>
            <strong>Upload User Pose (.npy):</strong>
          </label>
          <input type="file" accept=".npy" onChange={(e) => handleFileChange(e, setUserFile)} />
        </div>
        <div>
          <label>
            <strong>Upload Pro Pose (.npy):</strong>
          </label>
          <input type="file" accept=".npy" onChange={(e) => handleFileChange(e, setProFile)} />
        </div>

        <h3>User Key Events</h3>
        {Object.keys(userKeyEvents).map((key) => (
          <div key={key}>
            <label>
              {key.replace(/([A-Z])/g, " $1").replace(/^./, (str) => str.toUpperCase())} (seconds):
            </label>
            <input
              type="number"
              step="0.01"
              name={key}
              value={userKeyEvents[key]}
              onChange={(e) => handleKeyEventsChange(e, setUserKeyEvents)}
            />
          </div>
        ))}

        <h3>Pro Key Events</h3>
        {Object.keys(proKeyEvents).map((key) => (
          <div key={key}>
            <label>
              {key.replace(/([A-Z])/g, " $1").replace(/^./, (str) => str.toUpperCase())} (seconds):
            </label>
            <input
              type="number"
              step="0.01"
              name={key}
              value={proKeyEvents[key]}
              onChange={(e) => handleKeyEventsChange(e, setProKeyEvents)}
            />
          </div>
        ))}

        <h3>Select Key Event to Analyze</h3>
        <select
          value={selectedKeyEvent}
          onChange={(e) => setSelectedKeyEvent(e.target.value)}
          style={{ marginBottom: "20px", padding: "5px" }}
        >
          <option value="">-- Select Key Event --</option>
          <option value="ball_release">Ball Release</option>
          <option value="trophy_position">Trophy Position</option>
          <option value="racquet_low_point">Racquet Low Point</option>
          <option value="impact">Impact</option>
        </select>

        <button type="submit" style={{ marginTop: "20px", padding: "10px 20px" }}>
          Analyze Serve
        </button>
      </form>

      {analysisResult && analysisResult.length > 0 && (
        <div style={{ marginTop: "20px" }}>
          <h2>Analysis Result:</h2>
          <ul style={{ listStyleType: "none", padding: 0 }}>
            {analysisResult.map((line, index) => (
              <li
                key={index}
                style={{
                  marginBottom: "8px",
                  padding: "10px",
                  border: "1px solid #ddd",
                  borderRadius: "5px",
                }}
              >
                {line}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default App;
