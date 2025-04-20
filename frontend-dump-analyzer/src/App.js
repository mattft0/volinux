import React, { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [error, setError] = useState("");
  const [dragActive, setDragActive] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [isUploading, setIsUploading] = useState(false);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      setFile(file);
      await handleUpload(file);
    }
  };

  const handleFileSelect = async (e) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setFile(file);
      await handleUpload(file);
    }
  };

  const handleUpload = async (fileToUpload) => {
    setError("");
    setUploadStatus(null);
    setIsUploading(true);

    const formData = new FormData();
    formData.append("file", fileToUpload);

    try {
      const response = await axios.post("http://localhost:8281/upload_dump/", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      setUploadStatus(response.data);
    } catch (err) {
      setError(err.response?.data?.error || "Une erreur est survenue lors de l'upload");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white flex flex-col items-center justify-center px-4 py-10">
      <div className="w-full max-w-2xl bg-slate-800/50 backdrop-blur-sm rounded-2xl shadow-2xl p-8 space-y-8 border border-slate-700/50">
        <div className="text-center space-y-4">
          <h1 className="text-5xl font-bold bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-500 text-transparent bg-clip-text">
            Analyse de Dump Linux
          </h1>
          <p className="text-slate-400 text-lg">
            Uploader un fichier dump pour extraire la version du noyau
          </p>
        </div>

        <div
          className={`border-3 border-dashed rounded-xl p-12 text-center transition-all duration-300 ${dragActive
            ? "border-cyan-500 bg-cyan-500/10"
            : "border-slate-600 hover:border-slate-500"
            }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <input
            type="file"
            accept="*/*"
            onChange={handleFileSelect}
            className="hidden"
            id="file-upload"
          />
          <label
            htmlFor="file-upload"
            className="cursor-pointer flex flex-col items-center space-y-4"
          >
            {isUploading ? (
              <div className="flex flex-col items-center">
                <svg
                  className="animate-spin h-12 w-12 text-cyan-400"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  ></circle>
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
                <span className="text-cyan-400 mt-4">Analyse en cours...</span>
              </div>
            ) : (
              <>
                <svg
                  className={`w-16 h-16 transition-colors duration-300 ${dragActive ? "text-cyan-400" : "text-slate-400"
                    }`}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1.5}
                    d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                  />
                </svg>
                <div className="text-center space-y-2">
                  <p
                    className={`text-xl font-medium transition-colors duration-300 ${dragActive ? "text-cyan-400" : "text-slate-300"
                      }`}
                  >
                    {file ? file.name : "Glissez-déposez votre fichier ici"}
                  </p>
                  <p className="text-sm text-slate-500">
                    ou cliquez pour sélectionner un fichier
                  </p>
                </div>
              </>
            )}
          </label>
        </div>

        {error && (
          <div className="mt-6 p-6 bg-rose-500/10 border border-rose-500/30 rounded-xl text-center animate-fade-in backdrop-blur-sm">
            <p className="text-rose-400">{error}</p>
          </div>
        )}

        {uploadStatus && (
          <div className="mt-8 space-y-6">
            <div className="bg-slate-800/50 rounded-xl shadow-md p-6 backdrop-blur-sm border border-slate-700/50">
              <h2 className="text-xl font-semibold mb-4 text-cyan-400">Informations système</h2>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="font-medium text-slate-400">Distribution:</p>
                  <p className="text-slate-300">
                    {uploadStatus.distribution} {uploadStatus.distro_version}
                  </p>
                </div>
                <div>
                  <p className="font-medium text-slate-400">Version du noyau:</p>
                  <p className="text-slate-300">{uploadStatus.kernel_version}</p>
                </div>
              </div>
            </div>

            <div className="text-center">
              <a
                href="http://localhost:8281/results"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-block bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white font-bold py-3 px-6 rounded-xl transition-all duration-300 shadow-lg hover:shadow-cyan-500/20"
              >
                Voir les détails de l'analyse
              </a>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
