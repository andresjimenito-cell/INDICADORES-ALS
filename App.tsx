import React, { useState, useMemo } from 'react';
import { ConfigPanel } from './components/ConfigPanel';
import { DiagramCanvas } from './components/DiagramCanvas';
import { LandingPage } from './components/LandingPage';
import { CurveAnalysis } from './components/CurveAnalysis';
import { ConfigState, MotorType, WellPreset, WellStatus } from './types';
import { SliderControl } from './components/Controls';
import { Search, Filter, Menu, X, Settings2, LayoutDashboard, Database, ChevronRight, Droplets, ArrowLeft, UploadCloud } from 'lucide-react';

type ViewMode = 'HOME' | 'UPLOAD' | 'DASHBOARD' | 'DESIGN';
type FilterType = 'ALL' | 'RUNNING' | 'FAILED' | 'PULLED';

const App = () => {
  const [viewMode, setViewMode] = useState<ViewMode>('HOME');
  const [allWells, setAllWells] = useState<WellPreset[]>([]);
  const [selectedWellId, setSelectedWellId] = useState<string | null>(null);
  const [filter, setFilter] = useState<FilterType>('ALL');
  const [searchTerm, setSearchTerm] = useState(''); // State for search
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isControlsOpen, setIsControlsOpen] = useState(false); // State for minimized controls
  const [showCurveAnalysis, setShowCurveAnalysis] = useState(true); // Default to TRUE (Always visible)

  // Configuration State for Visualization
  const [config, setConfig] = useState<ConfigState>({
    zoom: 0.7,
    vsdFreq: 50,
    fluidLevel: 80,
    pip: 1000,
    cableSize: 4,
    yTool: false,
    motorType: MotorType.AMM,
    motorHp: 100,
    stagesUpper: 0,
    stagesLower: 0,
    sensor: false,
  });

  const handleNavigate = (mode: 'UPLOAD' | 'DESIGN') => {
      setViewMode(mode);
  };

  const handleDataLoaded = (wells: WellPreset[]) => {
    setAllWells(wells);
    if (wells.length > 0) {
      selectWell(wells[0]);
    }
    setViewMode('DASHBOARD');
  };

  const selectWell = (well: WellPreset) => {
    setSelectedWellId(well.id);
    setConfig(prev => ({
      ...prev,
      ...well,
      wellName: well.name,
      vsdFreq: well.vsdFreq || 50,
      fluidLevel: well.fluidLevel || 80,
      zoom: prev.zoom 
    }));
  };

  const handleConfigChange = (key: keyof ConfigState, value: any) => {
    setConfig((prev) => ({ ...prev, [key]: value }));
  };

  // Filter Logic including Search
  const filteredWells = useMemo(() => {
    let result = allWells;
    
    // 1. Filter by Status tag
    if (filter !== 'ALL') {
      result = result.filter(w => w.status === filter);
    }
    
    // 2. Filter by Search Term
    if (searchTerm.trim() !== '') {
      const lowerTerm = searchTerm.toLowerCase();
      result = result.filter(w => 
        w.name.toLowerCase().includes(lowerTerm) || 
        String(w.runNumber).toLowerCase().includes(lowerTerm)
      );
    }
    
    return result;
  }, [allWells, filter, searchTerm]);

  const counts = useMemo(() => ({
    ALL: allWells.length,
    RUNNING: allWells.filter(w => w.status === 'RUNNING').length,
    FAILED: allWells.filter(w => w.status === 'FAILED').length,
    PULLED: allWells.filter(w => w.status === 'PULLED').length,
  }), [allWells]);

  const getStatusColor = (status?: string) => {
    switch (status) {
        case 'RUNNING': return 'bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.5)]';
        case 'FAILED': return 'bg-red-500 shadow-[0_0_10px_rgba(239,68,68,0.5)]';
        case 'PULLED': return 'bg-slate-500';
        default: return 'bg-orange-400';
    }
  };

  // --- RENDER VIEWS ---

  if (viewMode === 'HOME') {
      return <LandingPage onNavigate={handleNavigate} />;
  }

  if (viewMode === 'DESIGN') {
      return (
          <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center text-white relative overflow-hidden">
              {/* Background ambient */}
              <div className="absolute top-[-20%] right-[-10%] w-[50%] h-[50%] bg-emerald-900/20 rounded-full blur-[120px] pointer-events-none"></div>
              
              <button 
                onClick={() => setViewMode('HOME')}
                className="absolute top-6 left-6 flex items-center gap-2 text-slate-400 hover:text-white transition-colors bg-slate-900/50 border border-slate-800 p-3 rounded-xl backdrop-blur-sm"
              >
                <ArrowLeft className="w-5 h-5" />
                <span>Volver</span>
              </button>
              <div className="bg-slate-900/60 backdrop-blur-xl p-12 rounded-3xl border border-slate-800 flex flex-col items-center text-center max-w-lg shadow-2xl relative z-10">
                  <div className="w-20 h-20 bg-emerald-500/10 rounded-full flex items-center justify-center mb-6 border border-emerald-500/20 shadow-[0_0_30px_rgba(16,185,129,0.1)]">
                      <Settings2 className="w-10 h-10 text-emerald-400" />
                  </div>
                  <h2 className="text-2xl font-bold mb-2 bg-clip-text text-transparent bg-gradient-to-r from-emerald-200 to-cyan-200">Módulo de Diseño</h2>
                  <p className="text-slate-400">Esta funcionalidad estará disponible en la próxima versión del proyecto ALS Frontera Energy.</p>
              </div>
          </div>
      );
  }

  if (viewMode === 'UPLOAD') {
    return <ConfigPanel onDataLoaded={handleDataLoaded} onBack={() => setViewMode('HOME')} />;
  }

  return (
    <div className="flex h-screen w-full bg-slate-950 overflow-hidden text-slate-200 font-sans">
      
      {/* SIDEBAR DRAWER - DEEP DARK GLASS THEME */}
      <aside 
        className={`${isSidebarOpen ? 'w-80' : 'w-0'} bg-slate-900/80 backdrop-blur-md border-r border-slate-800 flex flex-col transition-all duration-300 ease-in-out relative z-30 shadow-2xl`}
      >
        <div className="p-5 border-b border-slate-800 flex justify-between items-center bg-slate-900/50 min-h-[70px]">
            <div className="flex items-center gap-3">
              <div className="bg-orange-600/20 p-2 rounded-lg border border-orange-500/20">
                  <Database className="w-4 h-4 text-orange-400" />
              </div>
              <div>
                <h2 className="text-sm font-black text-white uppercase tracking-wider">Pozos</h2>
                <p className="text-[10px] text-slate-500 font-medium">DB: Active Session</p>
              </div>
            </div>
            <button onClick={() => setViewMode('UPLOAD')} className="text-slate-500 hover:text-orange-400 transition-colors p-2 hover:bg-slate-800 rounded-lg" title="Cargar otro archivo">
               <UploadCloud className="w-5 h-5" />
            </button>
        </div>

        {/* SEARCH BAR */}
        <div className="p-4 bg-transparent">
           <div className="relative group">
             <input 
                type="text" 
                placeholder="Buscar pozo..." 
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-3 py-2.5 bg-slate-800/50 border border-slate-700/50 rounded-xl text-sm font-medium text-slate-200 outline-none focus:ring-1 focus:ring-orange-500 focus:border-orange-500/50 transition-all placeholder:text-slate-600 group-hover:bg-slate-800"
             />
             <Search className="w-4 h-4 text-slate-500 absolute left-3 top-3 group-hover:text-orange-400 transition-colors" />
           </div>
        </div>

        {/* Quick Filters */}
        <div className="px-4 pb-2 grid grid-cols-4 gap-2 z-10">
            {(['ALL', 'RUNNING', 'FAILED', 'PULLED'] as FilterType[]).map(f => (
                <button 
                  key={f}
                  onClick={() => setFilter(f)}
                  className={`flex flex-col items-center justify-center py-2 rounded-xl transition-all border ${filter === f ? 'bg-orange-500/10 text-orange-300 border-orange-500/30 shadow-inner' : 'bg-slate-800/30 hover:bg-slate-800 text-slate-500 border-transparent hover:border-slate-700'}`}
                >
                    <span className={`text-lg font-bold leading-none ${filter === f ? 'text-orange-400' : 'text-slate-400'}`}>{counts[f]}</span>
                    <span className="text-[8px] font-bold uppercase mt-1 tracking-wider">{f === 'ALL' ? 'TODOS' : f}</span>
                </button>
            ))}
        </div>

        {/* Well List */}
        <div className="flex-1 overflow-y-auto p-3 space-y-1.5 custom-scrollbar bg-transparent">
            {filteredWells.map(well => (
                <button
                    key={well.id}
                    onClick={() => selectWell(well)}
                    className={`w-full text-left p-3.5 rounded-2xl border transition-all duration-200 group relative overflow-hidden ${selectedWellId === well.id ? 'bg-orange-600/10 border-orange-500/30 shadow-lg' : 'bg-slate-800/20 border-transparent hover:bg-slate-800/60 hover:border-slate-700'}`}
                >
                    {selectedWellId === well.id && <div className="absolute left-0 top-0 bottom-0 w-1 bg-orange-500 shadow-[0_0_10px_#f97316]"></div>}
                    <div className="flex justify-between items-start mb-1.5 pl-2">
                        <span className={`font-bold text-sm ${selectedWellId === well.id ? 'text-white' : 'text-slate-300 group-hover:text-orange-300'}`}>{well.name}</span>
                        <div className={`h-2 w-2 rounded-full ${getStatusColor(well.status)} mt-1.5`}></div>
                    </div>
                    <div className={`text-[10px] flex justify-between pl-2 ${selectedWellId === well.id ? 'text-orange-200/70' : 'text-slate-500'}`}>
                        <div className="flex items-center gap-2">
                            <span className="font-mono bg-slate-950/30 px-1.5 py-0.5 rounded text-[9px] border border-white/5">Run #{well.runNumber}</span>
                        </div>
                        <span>{well.installDate}</span>
                    </div>
                </button>
            ))}
            {filteredWells.length === 0 && (
                <div className="flex flex-col items-center justify-center py-20 text-slate-600 text-xs">
                    <Database className="w-10 h-10 mb-3 opacity-20" />
                    <p>No se encontraron pozos.</p>
                </div>
            )}
        </div>
      </aside>

      {/* MAIN CONTENT AREA */}
      <main className="flex-1 relative flex flex-col overflow-hidden bg-slate-950">
        
        {/* Background Ambience Layers */}
        <div className="absolute inset-0 z-0 pointer-events-none overflow-hidden">
            {/* Dark Noise Texture */}
            <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-5 mix-blend-overlay"></div>
            {/* Ambient Blobs */}
            <div className="absolute top-[-10%] right-[10%] w-[40%] h-[40%] bg-orange-900/10 rounded-full blur-[120px]"></div>
            <div className="absolute bottom-[-10%] left-[20%] w-[30%] h-[30%] bg-amber-900/10 rounded-full blur-[100px]"></div>
        </div>

        {/* Toggle Sidebar Button (Floating Top Left) */}
        <button 
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            className={`absolute top-5 left-5 z-20 bg-slate-900/80 backdrop-blur border border-slate-700 p-2.5 rounded-xl shadow-lg hover:bg-slate-800 text-slate-400 hover:text-white transition-all ${!isSidebarOpen && 'animate-pulse'}`}
            title="Mostrar/Ocultar Menú"
        >
            {isSidebarOpen ? <Menu className="w-5 h-5" /> : <ChevronRight className="w-5 h-5" />}
        </button>

        {/* MINIMIZABLE CONTROL PANEL */}
        <div className="absolute top-5 left-20 z-30 flex flex-col items-start transition-all duration-300">
            {/* Toggle Button */}
            <div className="flex gap-2">
                <button 
                    onClick={() => setIsControlsOpen(!isControlsOpen)}
                    className={`flex items-center gap-2 px-4 py-2.5 rounded-full shadow-xl border transition-all backdrop-blur-md ${isControlsOpen ? 'bg-orange-600/90 text-white border-orange-500 mb-3 shadow-orange-900/20' : 'bg-slate-900/80 text-slate-300 border-slate-700 hover:scale-105 hover:bg-slate-800'}`}
                >
                    <Settings2 className="w-4 h-4" />
                    <span className="text-xs font-bold uppercase tracking-wide">{isControlsOpen ? 'Ocultar' : 'Configuración'}</span>
                </button>
            </div>

            {/* Expanded Panel */}
            {isControlsOpen && (
                <div className="w-72 bg-slate-900/90 backdrop-blur-xl p-6 rounded-3xl shadow-2xl border border-slate-700/80 text-white animate-in slide-in-from-top-2 fade-in duration-200 origin-top-left ring-1 ring-white/5">
                    <div className="flex justify-between items-center mb-6 border-b border-white/5 pb-2">
                        <h3 className="text-[10px] font-black text-orange-400 uppercase tracking-widest flex items-center gap-2">
                            <Sliders className="w-3 h-3" /> Visual Controls
                        </h3>
                    </div>
                    
                    <div className="space-y-1">
                        <SliderControl label="Zoom General" value={config.zoom} min={0.5} max={1.8} step={0.1} unit="x" onChange={(v) => handleConfigChange('zoom', v)} />
                    </div>
                </div>
            )}
        </div>

        {/* FLOATING CURVE ANALYSIS WINDOW */}
        {showCurveAnalysis && (
            <CurveAnalysis config={config} onUpdateConfig={handleConfigChange} onClose={() => {}} />
        )}

        {/* Canvas Container - Full Width / Infinite Canvas Style - DARK BG */}
        <div className="flex-1 overflow-auto relative flex justify-center items-start pt-10 scroll-smooth bg-transparent z-0">
             <div 
               className="transition-transform duration-200 ease-out origin-top will-change-transform" 
               style={{ transform: `scale(${config.zoom})`, transformOrigin: 'top center' }}
             >
                <DiagramCanvas config={config} />
             </div>
        </div>

      </main>
    </div>
  );
};

// Simple Icon component for Controls to avoid import issues in pure copy-paste if needed
const Sliders = ({ className }: { className?: string }) => (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" /></svg>
);

export default App;