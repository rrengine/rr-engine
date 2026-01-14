/**
 * Specifications Panel Component
 *
 * Allows users to input and adjust instrumental specifications
 * for shoe geometry generation.
 */

import type { InstrumentalSpecs } from '../types';
import { SPEC_CONSTRAINTS, DEFAULT_INSTRUMENTAL_SPECS } from '../types';

interface SpecSliderProps {
  label: string;
  value: number;
  min: number;
  max: number;
  step: number;
  onChange: (value: number) => void;
  disabled?: boolean;
}

function SpecSlider({ label, value, min, max, step, onChange, disabled = false }: SpecSliderProps) {
  return (
    <div className="flex flex-col gap-1">
      <div className="flex justify-between items-center">
        <label className="text-sm text-gray-300">{label}</label>
        <span className="text-sm font-mono text-blue-400">{value}</span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        disabled={disabled}
        className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer
                   disabled:opacity-50 disabled:cursor-not-allowed
                   [&::-webkit-slider-thumb]:appearance-none
                   [&::-webkit-slider-thumb]:w-4
                   [&::-webkit-slider-thumb]:h-4
                   [&::-webkit-slider-thumb]:rounded-full
                   [&::-webkit-slider-thumb]:bg-blue-500
                   [&::-webkit-slider-thumb]:cursor-pointer
                   [&::-webkit-slider-thumb]:hover:bg-blue-400"
      />
      <div className="flex justify-between text-xs text-gray-500">
        <span>{min}</span>
        <span>{max}</span>
      </div>
    </div>
  );
}

interface SpecsPanelProps {
  specs: InstrumentalSpecs;
  onChange: (specs: InstrumentalSpecs) => void;
  onGenerate: () => void;
  isGenerating?: boolean;
  geometryHash?: string | null;
}

export function SpecsPanel({
  specs,
  onChange,
  onGenerate,
  isGenerating = false,
  geometryHash,
}: SpecsPanelProps) {
  const handleSpecChange = (key: keyof InstrumentalSpecs) => (value: number) => {
    onChange({ ...specs, [key]: value });
  };

  const handleReset = () => {
    onChange(DEFAULT_INSTRUMENTAL_SPECS);
  };

  return (
    <div className="flex flex-col gap-6 p-6 bg-gray-800 rounded-lg">
      <div className="flex justify-between items-center">
        <h2 className="text-lg font-semibold text-white">Instrumental Specs</h2>
        <button
          onClick={handleReset}
          className="text-sm text-gray-400 hover:text-white transition-colors"
        >
          Reset
        </button>
      </div>

      <div className="flex flex-col gap-4">
        {(Object.keys(SPEC_CONSTRAINTS) as Array<keyof typeof SPEC_CONSTRAINTS>).map((key) => {
          const constraint = SPEC_CONSTRAINTS[key];
          return (
            <SpecSlider
              key={key}
              label={constraint.label}
              value={specs[key]}
              min={constraint.min}
              max={constraint.max}
              step={constraint.step}
              onChange={handleSpecChange(key)}
              disabled={isGenerating}
            />
          );
        })}
      </div>

      <button
        onClick={onGenerate}
        disabled={isGenerating}
        className="w-full py-3 px-4 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-600
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
          'Generate Geometry'
        )}
      </button>

      {geometryHash && (
        <div className="flex flex-col gap-1 pt-4 border-t border-gray-700">
          <span className="text-xs text-gray-500">Geometry Hash</span>
          <code className="text-sm font-mono text-green-400 break-all">{geometryHash}</code>
        </div>
      )}
    </div>
  );
}

export default SpecsPanel;
