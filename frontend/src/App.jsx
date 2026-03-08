import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { UploadCloud, FileText, CheckSquare, AlignLeft, RefreshCw, X, History, ArrowRight } from 'lucide-react';

function App() {
  const [file, setFile] = useState(null);
  const [filePreview, setFilePreview] = useState('');
  const [isDragging, setIsDragging] = useState(false);
  
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('corrected');
  
  const [history, setHistory] = useState([]);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);
  
  const fileInputRef = useRef(null);

  // Load history on mount
  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const res = await axios.get('http://localhost:8000/api/history');
      if (res.data.history) {
        setHistory(res.data.history);
      }
    } catch (err) {
      console.error("Failed to load history", err);
    }
  };

  const clearSelection = () => {
    setFile(null);
    setFilePreview('');
    setResults(null);
    setError('');
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelected(e.dataTransfer.files[0]);
    }
  };

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelected(e.target.files[0]);
    }
  };

  const handleFileSelected = (selectedFile) => {
    if (!selectedFile.type.startsWith('image/')) {
      setError('Please upload a valid image file (JPG/PNG).');
      return;
    }
    setFile(selectedFile);
    setFilePreview(URL.createObjectURL(selectedFile));
    setResults(null);
    setError('');
  };

  const processImage = async () => {
    if (!file) return;
    
    setLoading(true);
    setError('');
    
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:8000/api/digitize', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setResults(response.data);
      fetchHistory(); // Refresh history with new entry
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred during processing.');
    } finally {
      setLoading(false);
    }
  };

  const loadHistoryItem = (item) => {
    setResults({
      raw_text: item.raw_text,
      corrected_text: item.corrected_text,
      todos: item.todos,
    });
    setFile(null); // Clear current file view and favor history item
    setFilePreview('');
    setIsHistoryOpen(false);
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
  };

  const downloadText = (text, filename) => {
    const element = document.createElement("a");
    const fileBlob = new Blob([text], {type: 'text/plain'});
    element.href = URL.createObjectURL(fileBlob);
    element.download = filename;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  return (
    <div className="min-h-screen flex flex-col relative w-full overflow-x-hidden">
      
      {/* Navbar */}
      <nav className="border-b bg-white px-6 py-4 flex items-center justify-between sticky top-0 z-40">
        <div className="font-bold text-xl tracking-tight text-slate-800 flex items-center gap-2">
          <FileText className="text-blue-600" />
          Scribble<span className="text-blue-600">Digital</span>
        </div>
        <button 
          onClick={() => setIsHistoryOpen(true)}
          className="flex items-center gap-2 text-sm font-medium text-slate-600 hover:text-slate-900 bg-slate-100 hover:bg-slate-200 px-4 py-2 rounded-md transition-colors"
        >
          <History size={16} />
          View History
        </button>
      </nav>

      {/* History Sidebar */}
      <div className={`fixed inset-y-0 right-0 w-80 bg-white shadow-2xl z-50 transform transition-transform duration-300 ease-in-out ${isHistoryOpen ? 'translate-x-0' : 'translate-x-full'}`}>
        <div className="p-4 border-b flex justify-between items-center bg-slate-50">
          <h2 className="font-semibold text-slate-800 flex items-center gap-2"><History size={18}/> Past Scans</h2>
          <button onClick={() => setIsHistoryOpen(false)} className="text-slate-400 hover:text-slate-700">
            <X size={20} />
          </button>
        </div>
        <div className="p-4 overflow-y-auto h-full pb-20">
          {history.length > 0 ? (
            <div className="flex flex-col gap-3">
              {history.map((item) => (
                <button 
                  key={item.id}
                  onClick={() => loadHistoryItem(item)}
                  className="text-left p-3 rounded-lg border border-slate-200 hover:border-blue-300 hover:bg-blue-50 transition-colors group"
                >
                  <p className="text-xs text-slate-500 mb-1">{item.timestamp}</p>
                  <p className="text-sm font-medium text-slate-800 truncate">
                    {item.corrected_text.substring(0, 40) || 'Empty Scan'}...
                  </p>
                </button>
              ))}
            </div>
          ) : (
            <p className="text-sm text-slate-500 text-center mt-10">No history found.</p>
          )}
        </div>
      </div>
      {/* Overlay when History is open */}
      {isHistoryOpen && (
        <div className="fixed inset-0 bg-slate-900/20 backdrop-blur-sm z-40" onClick={() => setIsHistoryOpen(false)}></div>
      )}

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-10 space-y-16">
        
        {/* HERO SECTION */}
        <section className="text-center space-y-6 pt-10 pb-8">
          <h1 className="text-5xl md:text-6xl font-extrabold text-slate-900 tracking-tight">
            Handwriting to <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">Structured Data</span>
          </h1>
          <p className="text-xl text-slate-600 max-w-2xl mx-auto leading-relaxed">
            Upload messy notes, whiteboard sketches, or journal entries. Our AI engine instantly enhances, transcribes, and extracts actionable tasks.
          </p>
        </section>

        {/* WORKSPACE SECTION */}
        <section className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 md:p-8">
          
          {!file && !results && (
            <div className="grid md:grid-cols-2 gap-10 items-center">
              {/* Feature Columns */}
              <div className="space-y-8">
                <div className="flex gap-4">
                  <div className="bg-blue-100 p-3 rounded-lg text-blue-700 h-fit"><UploadCloud /></div>
                  <div>
                    <h3 className="font-semibold text-lg text-slate-900">1. Upload Image</h3>
                    <p className="text-slate-600 mt-1 text-sm">Drag and drop a clear photo of your handwritten document.</p>
                  </div>
                </div>
                <div className="flex gap-4">
                  <div className="bg-emerald-100 p-3 rounded-lg text-emerald-700 h-fit"><AlignLeft /></div>
                  <div>
                    <h3 className="font-semibold text-lg text-slate-900">2. AI Transcription</h3>
                    <p className="text-slate-600 mt-1 text-sm">Computer vision and generative AI reconstruct unclear context automatically.</p>
                  </div>
                </div>
                <div className="flex gap-4">
                  <div className="bg-purple-100 p-3 rounded-lg text-purple-700 h-fit"><CheckSquare /></div>
                  <div>
                    <h3 className="font-semibold text-lg text-slate-900">3. Tasks Extracted</h3>
                    <p className="text-slate-600 mt-1 text-sm">Action items are segmented into a downloadable checklist.</p>
                  </div>
                </div>
              </div>

              {/* Upload Dropzone */}
              <div 
                className={`border-2 border-dashed rounded-xl flex flex-col items-center justify-center p-10 h-72 transition-colors cursor-pointer ${isDragging ? 'border-blue-500 bg-blue-50' : 'border-slate-300 bg-slate-50 hover:bg-slate-100'}`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
              >
                <div className="bg-white p-4 rounded-full shadow-sm mb-4">
                  <UploadCloud className="text-blue-600" size={32} />
                </div>
                <p className="font-semibold text-slate-800 text-lg">Click to upload or drag and drop</p>
                <p className="text-slate-500 text-sm mt-2">SVG, PNG, JPG or WEBP (max. 800x400px)</p>
                <input 
                  type="file" 
                  className="hidden" 
                  ref={fileInputRef} 
                  onChange={handleFileInput}
                  accept="image/jpeg, image/png, image/webp" 
                />
              </div>
            </div>
          )}

          {/* ACTIVE UPLOAD / PROCESSING STAGE */}
          {(file || results) && (
            <div className="flex flex-col xl:flex-row gap-8">
              
              {/* Left Column: Image Context */}
              <div className="xl:w-1/3 flex flex-col gap-4">
                <div className="flex items-center justify-between">
                  <h3 className="font-semibold text-slate-800">Source Document</h3>
                  <button onClick={clearSelection} className="text-xs text-slate-500 hover:text-slate-800 underline">Start Over</button>
                </div>
                
                {filePreview ? (
                  <div className="rounded-xl overflow-hidden border border-slate-200 bg-slate-50 flex items-center justify-center h-auto">
                    <img src={filePreview} alt="Preview" className="w-full h-auto object-contain max-h-[500px]" />
                  </div>
                ) : (
                  <div className="rounded-xl border border-slate-200 bg-slate-50 p-6 flex flex-col items-center justify-center text-center h-[300px]">
                    <History className="text-slate-400 mb-2" size={32} />
                    <p className="text-slate-600 text-sm">Viewing historical scan.</p>
                    <p className="text-slate-400 text-xs mt-1">Original image not saved.</p>
                  </div>
                )}

                {!results && file && (
                  <button 
                    onClick={processImage}
                    disabled={loading}
                    className="w-full mt-4 bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-4 rounded-lg transition-colors flex justify-center items-center gap-2 disabled:bg-blue-400"
                  >
                    {loading ? (
                      <><RefreshCw className="animate-spin" size={20} /> Processing AI Models...</>
                    ) : (
                      <>Digitize Document <ArrowRight size={20} /></>
                    )}
                  </button>
                )}

                {error && (
                  <div className="mt-4 p-4 bg-red-50 text-red-700 rounded-lg text-sm border border-red-100">
                    <p className="font-semibold">Error processing image</p>
                    <p>{error}</p>
                  </div>
                )}
              </div>

              {/* Right Column: Results */}
              <div className="xl:w-2/3 flex flex-col border border-slate-200 rounded-xl overflow-hidden">
                {results ? (
                  <>
                    <div className="flex border-b border-slate-200 bg-slate-50">
                      <button 
                        className={`flex-1 py-3 text-sm font-medium transition-colors border-b-2 outline-none ${activeTab === 'corrected' ? 'border-blue-600 text-blue-700 bg-white' : 'border-transparent text-slate-600 hover:text-slate-900 hover:bg-slate-100'}`}
                        onClick={() => setActiveTab('corrected')}
                      >
                        Corrected Text
                      </button>
                      <button 
                        className={`flex-1 py-3 text-sm font-medium transition-colors border-b-2 outline-none ${activeTab === 'todos' ? 'border-blue-600 text-blue-700 bg-white' : 'border-transparent text-slate-600 hover:text-slate-900 hover:bg-slate-100'}`}
                        onClick={() => setActiveTab('todos')}
                      >
                        Actionable Tasks
                      </button>
                      <button 
                        className={`flex-1 py-3 text-sm font-medium transition-colors border-b-2 outline-none ${activeTab === 'raw' ? 'border-blue-600 text-blue-700 bg-white' : 'border-transparent text-slate-600 hover:text-slate-900 hover:bg-slate-100'}`}
                        onClick={() => setActiveTab('raw')}
                      >
                        Raw OCR
                      </button>
                    </div>

                    <div className="p-6 bg-white min-h-[400px] flex flex-col">
                      {activeTab === 'corrected' && (
                        <>
                          <div className="flex justify-end gap-2 mb-4">
                            <button onClick={() => copyToClipboard(results.corrected_text)} className="text-xs bg-slate-100 hover:bg-slate-200 text-slate-700 py-1.5 px-3 rounded-md transition-colors">Copy</button>
                            <button onClick={() => downloadText(results.corrected_text, 'corrected_notes.txt')} className="text-xs bg-blue-50 hover:bg-blue-100 text-blue-700 py-1.5 px-3 rounded-md transition-colors">Download</button>
                          </div>
                          <div className="whitespace-pre-wrap text-slate-800 leading-relaxed font-sans">{results.corrected_text}</div>
                        </>
                      )}
                      
                      {activeTab === 'todos' && (
                        <>
                          <div className="flex justify-end gap-2 mb-4">
                            <button onClick={() => copyToClipboard(results.todos)} className="text-xs bg-slate-100 hover:bg-slate-200 text-slate-700 py-1.5 px-3 rounded-md transition-colors">Copy</button>
                            <button onClick={() => downloadText(results.todos, 'tasks.txt')} className="text-xs bg-blue-50 hover:bg-blue-100 text-blue-700 py-1.5 px-3 rounded-md transition-colors">Download</button>
                          </div>
                          <div className="whitespace-pre-wrap text-slate-800 leading-relaxed font-sans">{results.todos}</div>
                        </>
                      )}

                      {activeTab === 'raw' && (
                        <>
                          <div className="flex justify-end gap-2 mb-4">
                            <button onClick={() => copyToClipboard(results.raw_text)} className="text-xs bg-slate-100 hover:bg-slate-200 text-slate-700 py-1.5 px-3 rounded-md transition-colors">Copy</button>
                          </div>
                          <div className="whitespace-pre-wrap text-slate-600 leading-relaxed font-mono text-sm bg-slate-50 p-4 rounded-lg">{results.raw_text}</div>
                        </>
                      )}
                    </div>
                  </>
                ) : (
                  <div className="flex-1 flex flex-col items-center justify-center p-10 text-center bg-slate-50 h-[500px]">
                    {loading ? (
                      <div className="space-y-4">
                        <RefreshCw className="animate-spin text-blue-600 mx-auto" size={40} />
                        <p className="text-slate-600 font-medium">Extracting and processing text...</p>
                        <p className="text-xs text-slate-400">This might take 5-10 seconds using AI models.</p>
                      </div>
                    ) : (
                      <div className="space-y-2 max-w-sm">
                        <div className="mx-auto w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mb-4 text-slate-400">
                          <AlertCircle size={24} />
                        </div>
                        <h3 className="font-semibold text-slate-800">Ready to Process</h3>
                        <p className="text-sm text-slate-500">Hit the "Digitize Document" button on the left to start the AI extraction.</p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          )}

        </section>

        {/* PROCESS SECTION */}
        <section className="py-20 border-t border-slate-200">
          <div className="text-center mb-16 px-4">
            <h2 className="text-3xl font-bold text-slate-900 tracking-tight">The Digital Transformation Process</h2>
            <p className="text-slate-600 mt-4 max-w-2xl mx-auto">From ink to insights. Our multi-stage pipeline ensures the highest accuracy for your handwritten data.</p>
          </div>
          
          <div className="grid md:grid-cols-4 gap-8">
            <div className="space-y-4">
              <div className="w-12 h-12 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold text-lg">1</div>
              <h4 className="font-semibold text-slate-800">Image Enhancement</h4>
              <p className="text-sm text-slate-600 leading-relaxed">Adaptive thresholding and noise reduction prep the image for optimal machine reading.</p>
            </div>
            <div className="space-y-4">
              <div className="w-12 h-12 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold text-lg">2</div>
              <h4 className="font-semibold text-slate-800">Neural OCR</h4>
              <p className="text-sm text-slate-600 leading-relaxed">Optical Character Recognition identifies raw glyphs and converts them into raw text strings.</p>
            </div>
            <div className="space-y-4">
              <div className="w-12 h-12 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold text-lg">3</div>
              <h4 className="font-semibold text-slate-800">LLM Reconstruction</h4>
              <p className="text-sm text-slate-600 leading-relaxed">Generative AI analyzes the text, fixing grammar, spelling, and missing context automatically.</p>
            </div>
            <div className="space-y-4">
              <div className="w-12 h-12 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold text-lg">4</div>
              <h4 className="font-semibold text-slate-800">Task Extraction</h4>
              <p className="text-sm text-slate-600 leading-relaxed">Action items are segmented using natural language understanding into actionable checklists.</p>
            </div>
          </div>
        </section>

        {/* WHY SCRIBBLE SECTION */}
        <section className="py-20 bg-slate-900 rounded-3xl px-8 md:px-16 text-white overflow-hidden relative">
          <div className="absolute top-0 right-0 w-64 h-64 bg-blue-600/20 blur-3xl rounded-full translate-x-1/2 -translate-y-1/2"></div>
          <div className="relative z-10 grid lg:grid-cols-2 gap-12 items-center">
            <div className="space-y-6">
              <h2 className="text-4xl font-bold tracking-tight">Focus on what matters, leave the typing to us.</h2>
              <p className="text-slate-300 text-lg leading-relaxed">
                Scribble to Digital turns your manual note-taking habits into a high-powered digital workflow. Perfect for students, researchers, and project managers.
              </p>
              <div className="grid grid-cols-2 gap-6 pt-4">
                <div className="space-y-1">
                  <p className="text-3xl font-bold text-blue-400">99%</p>
                  <p className="text-sm text-slate-400">Accuracy Rate</p>
                </div>
                <div className="space-y-1">
                  <p className="text-3xl font-bold text-blue-400">&lt; 5s</p>
                  <p className="text-sm text-slate-400">Processing Time</p>
                </div>
              </div>
            </div>
            <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 p-8 rounded-2xl space-y-4">
              <div className="flex gap-3 items-start">
                <div className="mt-1 text-emerald-400"><CheckSquare size={18}/></div>
                <p className="text-slate-200"><span className="font-semibold">Contextual Awareness:</span> AI understands common abbreviations and industry shorthand.</p>
              </div>
              <div className="flex gap-3 items-start">
                <div className="mt-1 text-emerald-400"><CheckSquare size={18}/></div>
                <p className="text-slate-200"><span className="font-semibold">Task Segmentation:</span> Automatically differentiates notes from actual to-dos.</p>
              </div>
              <div className="flex gap-3 items-start">
                <div className="mt-1 text-emerald-400"><CheckSquare size={18}/></div>
                <p className="text-slate-200"><span className="font-semibold">Local History:</span> Keep track of your past scans locally on your machine.</p>
              </div>
            </div>
          </div>
        </section>
      </main>
      
      {/* Footer */}
      <footer className="border-t bg-slate-50 mt-auto">
        <div className="max-w-7xl mx-auto px-4 py-6 text-center text-sm text-slate-500">
          Powered by React, FastAPI, OpenCV, and Generative AI.
        </div>
      </footer>
    </div>
  );
}

// Dummy component just to use when Results are unready without creating a separate file
function AlertCircle({ size }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10"></circle>
      <line x1="12" y1="8" x2="12" y2="12"></line>
      <line x1="12" y1="16" x2="12.01" y2="16"></line>
    </svg>
  );
}

export default App;
