/**
 * RR Engine - 3D Fashion Design Platform
 *
 * Main application component for the shoe design interface.
 */

import { useState, useCallback } from 'react';
import { ShoeViewer } from './components/ShoeViewer';
import { SpecsPanel } from './components/SpecsPanel';
import { MaterialsPanel } from './components/MaterialsPanel';
import type { InstrumentalSpecs, NonInstrumentalSpecs, GenerateResult } from './types';
import { DEFAULT_INSTRUMENTAL_SPECS, DEFAULT_NON_INSTRUMENTAL_SPECS } from './types';

function App() {
  const [specs, setSpecs] = useState<InstrumentalSpecs>(DEFAULT_INSTRUMENTAL_SPECS);
  const [materials, setMaterials] = useState<NonInstrumentalSpecs>(DEFAULT_NON_INSTRUMENTAL_SPECS);
  const [isGenerating, setIsGenerating] = useState(false);
  const [result, setResult] = useState<GenerateResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'geometry' | 'materials'>('geometry');

  const handleGenerate = useCallback(async () => {
    setIsGenerating(true);
    setError(null);

    try {
      const requestBody = {
        ...specs,
        materials: {
          upper_material: materials.materials.upper,
          sole_material: materials.materials.sole,
          upper_color: materials.colors.upper_color,
          sole_color: materials.colors.sole_color,
          accent_color: materials.colors.accent_color,
          roughness: materials.roughness,
          metallic: materials.metallic,
        },
      };

      const response = await fetch('/api/geometry/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Generation failed: ${response.status}`);
      }

      const data: GenerateResult = await response.json();
      setResult(data);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(message);
      console.error('Generation error:', err);
    } finally {
      setIsGenerating(false);
    }
  }, [specs, materials]);

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      {/* Header */}
      <header className="border-b border-gray-800 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg" />
            <h1 className="text-xl font-bold">RR Engine</h1>
            <span className="text-xs text-gray-500 bg-gray-800 px-2 py-1 rounded">v1.0</span>
          </div>
          <nav className="flex items-center gap-4">
            <span className="text-sm text-gray-400">3D Fashion Design Platform</span>
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* 3D Viewer - 2/3 width on large screens */}
          <div className="lg:col-span-2 flex flex-col gap-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold">3D Preview</h2>
              {result && (
                <div className="flex items-center gap-4 text-sm text-gray-400">
                  <span>{result.vertex_count.toLocaleString()} vertices</span>
                  <span>{result.face_count.toLocaleString()} faces</span>
                </div>
              )}
            </div>

            <ShoeViewer
              modelUrl={result?.mesh_uri}
              autoRotate={!isGenerating}
              className="aspect-video"
            />

            {/* Status Bar */}
            <div className="flex items-center justify-between px-4 py-3 bg-gray-800 rounded-lg">
              <div className="flex items-center gap-2">
                <div
                  className={`w-2 h-2 rounded-full ${
                    result ? 'bg-green-500' : 'bg-gray-500'
                  }`}
                />
                <span className="text-sm text-gray-300">
                  {result ? 'Geometry Ready' : 'No geometry generated'}
                </span>
              </div>
              {result && (
                <a
                  href={result.mesh_uri}
                  download
                  className="text-sm text-blue-400 hover:text-blue-300 transition-colors"
                >
                  Download GLB
                </a>
              )}
            </div>
          </div>

          {/* Controls Panel - 1/3 width on large screens */}
          <div className="flex flex-col gap-4">
            {/* Tab Switcher */}
            <div className="flex bg-gray-800 rounded-lg p-1">
              <button
                onClick={() => setActiveTab('geometry')}
                className={`flex-1 py-2 px-4 text-sm font-medium rounded-md transition-colors ${
                  activeTab === 'geometry'
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                Geometry
              </button>
              <button
                onClick={() => setActiveTab('materials')}
                className={`flex-1 py-2 px-4 text-sm font-medium rounded-md transition-colors ${
                  activeTab === 'materials'
                    ? 'bg-purple-600 text-white'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                Materials
              </button>
            </div>

            {/* Tab Content */}
            {activeTab === 'geometry' ? (
              <SpecsPanel
                specs={specs}
                onChange={setSpecs}
                onGenerate={handleGenerate}
                isGenerating={isGenerating}
                geometryHash={result?.geometry_hash}
              />
            ) : (
              <MaterialsPanel
                specs={materials}
                onChange={setMaterials}
              />
            )}

            {/* Generate Button (visible on Materials tab too) */}
            {activeTab === 'materials' && (
              <button
                onClick={handleGenerate}
                disabled={isGenerating}
                className="w-full py-3 px-4 bg-purple-600 hover:bg-purple-500 disabled:bg-gray-600
                           text-white font-medium rounded-lg transition-colors
                           disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {isGenerating ? (
                  <>
                    <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                        fill="none"
                      />
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                      />
                    </svg>
                    Generating...
                  </>
                ) : (
                  'Apply Materials & Generate'
                )}
              </button>
            )}

            {/* Error Display */}
            {error && (
              <div className="p-4 bg-red-900/50 border border-red-700 rounded-lg">
                <h3 className="text-sm font-medium text-red-400">Error</h3>
                <p className="text-sm text-red-300 mt-1">{error}</p>
              </div>
            )}

            {/* Info Cards */}
            {result && (
              <div className="p-4 bg-gray-800 rounded-lg">
                <h3 className="text-sm font-medium text-gray-300 mb-2">Generation Info</h3>
                <div className="space-y-2 text-xs">
                  <div className="flex justify-between">
                    <span className="text-gray-500">Geometry Hash:</span>
                    <code className="text-green-400">{result.geometry_hash}</code>
                  </div>
                  {result.material_hash && (
                    <div className="flex justify-between">
                      <span className="text-gray-500">Material Hash:</span>
                      <code className="text-purple-400">{result.material_hash}</code>
                    </div>
                  )}
                  <div className="flex justify-between">
                    <span className="text-gray-500">Bounds:</span>
                    <span className="text-gray-300 font-mono">
                      {result.bounds.max[0].toFixed(0)} x {result.bounds.max[1].toFixed(0)} x {result.bounds.max[2].toFixed(0)} mm
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-800 px-6 py-4 mt-8">
        <div className="max-w-7xl mx-auto flex items-center justify-between text-sm text-gray-500">
          <span>RR Engine - Production-Grade 3D Fashion Design</span>
          <span>Deterministic Geometry Generation</span>
        </div>
      </footer>
    </div>
  );
}

export default App;
