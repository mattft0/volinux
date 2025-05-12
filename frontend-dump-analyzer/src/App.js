import React, { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [error, setError] = useState("");
  const [dragActive, setDragActive] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isExecutingPlugin, setIsExecutingPlugin] = useState(false);
  const [selectedPlugin, setSelectedPlugin] = useState("");
  const [language, setLanguage] = useState("en");

  const translations = {
    en: {
      title: "Linux Dump Analysis",
      subtitle: "Upload a dump file to extract kernel version",
      dragDrop: "Drag and drop your file here",
      orClick: "or click to select a file",
      analyzing: "Analyzing...",
      systemInfo: "System Information",
      distribution: "Distribution:",
      kernelVersion: "Kernel Version:",
      availablePlugins: "Available Plugins",
      selectPlugin: "Select a plugin",
      startAnalysis: "Start Analysis",
      analysisInProgress: "Analysis in progress...",
      uploadError: "An error occurred during upload",
      pluginError: "An error occurred during plugin execution"
    },
    fr: {
      title: "Analyse de Dump Linux",
      subtitle: "Uploader un fichier dump pour extraire la version du noyau",
      dragDrop: "Glissez-déposez votre fichier ici",
      orClick: "ou cliquez pour sélectionner un fichier",
      analyzing: "Analyse en cours...",
      systemInfo: "Informations système",
      distribution: "Distribution:",
      kernelVersion: "Version du noyau:",
      availablePlugins: "Plugins disponibles",
      selectPlugin: "Sélectionnez un plugin",
      startAnalysis: "Démarrer l'analyse",
      analysisInProgress: "Analyse en cours...",
      uploadError: "Une erreur est survenue lors de l'upload",
      pluginError: "Une erreur est survenue lors de l'exécution du plugin"
    }
  };

  const t = translations[language];

  const plugins = [
    { name: "Bash History", command: "linux.bash" },
    { name: "Environment Variables", command: "linux.envars" },
    { name: "IP Addresses", command: "linux.ip.Addr" },
    { name: "Networks Infos", command: "linux.ip.Link" },
    { name: "Boottime Infos", command: "linux.boottime.Boottime" },
    { name: "List File in Memory", command: "linux.pagecache.Files" },
    { name: "Process List", command: "linux.pslist.PsList" }
  ];

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
      const response = await axios.post("http://localhost:8000/upload_dump/", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      setUploadStatus(response.data);
    } catch (err) {
      setError(err.response?.data?.error || t.uploadError);
    } finally {
      setIsUploading(false);
    }
  };

  const handlePluginExecution = async (pluginCommand) => {
    setError("");
    setIsExecutingPlugin(true);

    try {
      const response = await axios.get(`http://localhost:8000/execute_plugin/${pluginCommand}`);
      if (response.data.success) {
        window.open("http://localhost:8000/results", "_blank");
      }
    } catch (err) {
      setError(err.response?.data?.error || t.pluginError);
    } finally {
      setIsExecutingPlugin(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white flex flex-col items-center justify-center px-4 py-10">
      <div className="w-full max-w-2xl bg-slate-800/50 backdrop-blur-sm rounded-2xl shadow-2xl p-8 space-y-8 border border-slate-700/50">
        <div className="flex justify-end mb-4">
          <button
            onClick={() => setLanguage(language === "en" ? "fr" : "en")}
            className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg transition-colors duration-300"
          >
            {language === "en" ? "FR" : "EN"}
          </button>
        </div>

        <div className="text-center space-y-4">
          <h1 className="text-5xl font-bold bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-500 text-transparent bg-clip-text">
            {t.title}
          </h1>
          <p className="text-slate-400 text-lg">
            {t.subtitle}
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
                <span className="text-cyan-400 mt-4">{t.analyzing}</span>
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
                    {file ? file.name : t.dragDrop}
                  </p>
                  <p className="text-sm text-slate-500">
                    {t.orClick}
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
              <h2 className="text-xl font-semibold mb-4 text-cyan-400">{t.systemInfo}</h2>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="font-medium text-slate-400">{t.distribution}</p>
                  <p className="text-slate-300">
                    {uploadStatus.distribution} {uploadStatus.distro_version}
                  </p>
                </div>
                <div>
                  <p className="font-medium text-slate-400">{t.kernelVersion}</p>
                  <p className="text-slate-300">{uploadStatus.kernel_version}</p>
                </div>
              </div>
            </div>

            <div className="mt-8">
              <h3 className="text-xl font-semibold mb-4 text-cyan-400">{t.availablePlugins}</h3>
              <div className="space-y-4">
                <select
                  value={selectedPlugin}
                  onChange={(e) => setSelectedPlugin(e.target.value)}
                  className="w-full bg-slate-700 border border-slate-600 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
                >
                  <option value="">{t.selectPlugin}</option>
                  {plugins.map((plugin) => (
                    <option key={plugin.command} value={plugin.command}>
                      {plugin.name}
                    </option>
                  ))}
                </select>
                <button
                  onClick={() => selectedPlugin && handlePluginExecution(selectedPlugin)}
                  disabled={isExecutingPlugin || !selectedPlugin}
                  className="w-full bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white font-bold py-3 px-6 rounded-xl transition-all duration-300 shadow-lg hover:shadow-cyan-500/20 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isExecutingPlugin ? t.analysisInProgress : t.startAnalysis}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;