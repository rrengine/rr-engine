/**
 * RR Engine - 3D Fashion Design Platform
 *
 * Main application component for the shoe design interface.
 */

import { useState, useCallback } from 'react';
import { ShoeViewer } from './components/ShoeViewer';
import { SpecsPanel } from './components/SpecsPanel';
import type { InstrumentalSpecs, GenerateResult } from './types';
import { DEFAULT_INSTRUMENTAL_SPECS } from './types';

function App() {
  const [specs, setSpecs] = useState<InstrumentalSpecs>(DEFAULT_INSTRUMENTAL_SPECS);
  const [isGenerating, setIsGenerating] = useState(false);
  const [result, setResult] = useState<GenerateResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = useCallback(async () => {
    setIsGenerating(true);
    setError(null);

    try {
      const response = await fetch('/api/geometry/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(specs),
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
  }, [specs]);

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

          {/* Specs Panel - 1/3 width on large screens */}
          <div className="flex flex-col gap-4">
            <SpecsPanel
              specs={specs}
              onChange={setSpecs}
              onGenerate={handleGenerate}
              isGenerating={isGenerating}
              geometryHash={result?.geometry_hash}
            />

            {/* Error Display */}
            {error && (
              <div className="p-4 bg-red-900/50 border border-red-700 rounded-lg">
                <h3 className="text-sm font-medium text-red-400">Error</h3>
                <p className="text-sm text-red-300 mt-1">{error}</p>
              </div>
            )}

            {/* Bounds Info */}
            {result && (
              <div className="p-4 bg-gray-800 rounded-lg">
                <h3 className="text-sm font-medium text-gray-300 mb-2">Bounding Box</h3>
                <div className="grid grid-cols-2 gap-2 text-xs font-mono">
                  <div>
                    <span className="text-gray-500">Min:</span>
                    <div className="text-gray-300">
                      [{result.bounds.min.map((v) => v.toFixed(1)).join(', ')}]
                    </div>
                  </div>
                  <div>
                    <span className="text-gray-500">Max:</span>
                    <div className="text-gray-300">
                      [{result.bounds.max.map((v) => v.toFixed(1)).join(', ')}]
                    </div>
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
