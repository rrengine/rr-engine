/**
 * Materials & Colors Panel Component
 *
 * Allows users to configure non-instrumental specifications:
 * materials, colors, roughness, and metallic properties.
 */

import type { NonInstrumentalSpecs } from '../types';
import { MATERIAL_OPTIONS, DEFAULT_NON_INSTRUMENTAL_SPECS } from '../types';

interface ColorPickerProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
}

function ColorPicker({ label, value, onChange }: ColorPickerProps) {
  return (
    <div className="flex items-center justify-between gap-3">
      <label className="text-sm text-gray-300">{label}</label>
      <div className="flex items-center gap-2">
        <input
          type="color"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="w-8 h-8 rounded cursor-pointer border border-gray-600 bg-transparent"
        />
        <input
          type="text"
          value={value.toUpperCase()}
          onChange={(e) => onChange(e.target.value)}
          className="w-20 px-2 py-1 text-xs font-mono bg-gray-700 border border-gray-600 rounded text-gray-300"
        />
      </div>
    </div>
  );
}

interface SelectProps {
  label: string;
  value: string;
  options: readonly { value: string; label: string }[];
  onChange: (value: string) => void;
}

function Select({ label, value, options, onChange }: SelectProps) {
  return (
    <div className="flex items-center justify-between gap-3">
      <label className="text-sm text-gray-300">{label}</label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="px-3 py-1.5 text-sm bg-gray-700 border border-gray-600 rounded text-gray-300 cursor-pointer"
      >
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
    </div>
  );
}

interface SliderProps {
  label: string;
  value: number;
  min: number;
  max: number;
  step: number;
  onChange: (value: number) => void;
}

function Slider({ label, value, min, max, step, onChange }: SliderProps) {
  return (
    <div className="flex flex-col gap-1">
      <div className="flex justify-between items-center">
        <label className="text-sm text-gray-300">{label}</label>
        <span className="text-sm font-mono text-blue-400">{value.toFixed(2)}</span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer
                   [&::-webkit-slider-thumb]:appearance-none
                   [&::-webkit-slider-thumb]:w-4
                   [&::-webkit-slider-thumb]:h-4
                   [&::-webkit-slider-thumb]:rounded-full
                   [&::-webkit-slider-thumb]:bg-purple-500
                   [&::-webkit-slider-thumb]:cursor-pointer
                   [&::-webkit-slider-thumb]:hover:bg-purple-400"
      />
    </div>
  );
}

interface MaterialsPanelProps {
  specs: NonInstrumentalSpecs;
  onChange: (specs: NonInstrumentalSpecs) => void;
}

export function MaterialsPanel({ specs, onChange }: MaterialsPanelProps) {
  const handleMaterialChange = (key: keyof typeof specs.materials) => (value: string) => {
    onChange({
      ...specs,
      materials: { ...specs.materials, [key]: value },
    });
  };

  const handleColorChange = (key: keyof typeof specs.colors) => (value: string) => {
    onChange({
      ...specs,
      colors: { ...specs.colors, [key]: value },
    });
  };

  const handleReset = () => {
    onChange(DEFAULT_NON_INSTRUMENTAL_SPECS);
  };

  return (
    <div className="flex flex-col gap-6 p-6 bg-gray-800 rounded-lg">
      <div className="flex justify-between items-center">
        <h2 className="text-lg font-semibold text-white">Materials & Colors</h2>
        <button
          onClick={handleReset}
          className="text-sm text-gray-400 hover:text-white transition-colors"
        >
          Reset
        </button>
      </div>

      {/* Materials Section */}
      <div className="flex flex-col gap-3">
        <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wide">Materials</h3>
        <Select
          label="Upper"
          value={specs.materials.upper}
          options={MATERIAL_OPTIONS.upper}
          onChange={handleMaterialChange('upper')}
        />
        <Select
          label="Sole"
          value={specs.materials.sole}
          options={MATERIAL_OPTIONS.sole}
          onChange={handleMaterialChange('sole')}
        />
      </div>

      {/* Colors Section */}
      <div className="flex flex-col gap-3">
        <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wide">Colors</h3>
        <ColorPicker
          label="Upper"
          value={specs.colors.upper_color}
          onChange={handleColorChange('upper_color')}
        />
        <ColorPicker
          label="Sole"
          value={specs.colors.sole_color}
          onChange={handleColorChange('sole_color')}
        />
        <ColorPicker
          label="Accent"
          value={specs.colors.accent_color}
          onChange={handleColorChange('accent_color')}
        />
      </div>

      {/* PBR Properties */}
      <div className="flex flex-col gap-3">
        <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wide">Surface</h3>
        <Slider
          label="Roughness"
          value={specs.roughness}
          min={0}
          max={1}
          step={0.05}
          onChange={(v) => onChange({ ...specs, roughness: v })}
        />
        <Slider
          label="Metallic"
          value={specs.metallic}
          min={0}
          max={1}
          step={0.05}
          onChange={(v) => onChange({ ...specs, metallic: v })}
        />
      </div>

      {/* Material Preview */}
      <div className="flex items-center gap-3 pt-4 border-t border-gray-700">
        <div
          className="w-12 h-12 rounded-lg border border-gray-600"
          style={{ backgroundColor: specs.colors.upper_color }}
          title="Upper color"
        />
        <div
          className="w-12 h-12 rounded-lg border border-gray-600"
          style={{ backgroundColor: specs.colors.sole_color }}
          title="Sole color"
        />
        <div
          className="w-12 h-12 rounded-lg border border-gray-600"
          style={{ backgroundColor: specs.colors.accent_color }}
          title="Accent color"
        />
        <div className="flex-1 text-xs text-gray-500">
          {specs.materials.upper} upper, {specs.materials.sole} sole
        </div>
      </div>
    </div>
  );
}

export default MaterialsPanel;
