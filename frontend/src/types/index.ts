/**
 * Type definitions for the RR Engine frontend.
 */

export interface InstrumentalSpecs {
  shoe_length_mm: number;
  shoe_width_mm: number;
  sole_thickness_mm: number;
  arch_height_mm: number;
  toe_spring_mm: number;
  collar_height_mm: number;
}

export interface MaterialSpecs {
  upper: string;
  sole: string;
}

export interface ColorSpecs {
  upper_color: string;
  sole_color: string;
  accent_color: string;
}

export interface NonInstrumentalSpecs {
  materials: MaterialSpecs;
  colors: ColorSpecs;
  roughness: number;
  metallic: number;
}

export const MATERIAL_OPTIONS = {
  upper: [
    { value: 'leather', label: 'Leather' },
    { value: 'suede', label: 'Suede' },
    { value: 'canvas', label: 'Canvas' },
    { value: 'mesh', label: 'Mesh' },
    { value: 'synthetic', label: 'Synthetic' },
    { value: 'knit', label: 'Knit' },
  ],
  sole: [
    { value: 'rubber', label: 'Rubber' },
    { value: 'foam', label: 'Foam (EVA)' },
    { value: 'leather', label: 'Leather' },
    { value: 'gum', label: 'Gum' },
    { value: 'translucent', label: 'Translucent' },
  ],
} as const;

export const DEFAULT_NON_INSTRUMENTAL_SPECS: NonInstrumentalSpecs = {
  materials: {
    upper: 'leather',
    sole: 'rubber',
  },
  colors: {
    upper_color: '#1a1a1a',
    sole_color: '#f5f5f5',
    accent_color: '#3b82f6',
  },
  roughness: 0.5,
  metallic: 0.0,
};

export interface GeometryAsset {
  mesh_uri: string;
  anchors_uri: string;
  bounds: {
    min: [number, number, number];
    max: [number, number, number];
  };
  geometry_hash: string;
}

export interface Generation {
  id: string;
  project_id: string;
  source: 'generate' | 'regenerate' | 'import' | 'ai_merge' | 'ai_draft' | 'factory_feedback';
  parent_ids: string[] | null;
  is_active: boolean;
  created_by: string;
  created_at: string;
}

export interface Project {
  id: string;
  owner_id: string;
  name: string;
  created_at: string;
}

export interface AnchorPoints {
  toe_box_center: [number, number, number];
  heel_center: [number, number, number];
  lateral_midfoot: [number, number, number];
  medial_midfoot: [number, number, number];
  tongue_top: [number, number, number];
  collar_back: [number, number, number];
}

export interface GenerateResult {
  mesh_uri: string;
  anchors_uri: string;
  bounds: {
    min: [number, number, number];
    max: [number, number, number];
  };
  geometry_hash: string;
  material_hash?: string | null;
  vertex_count: number;
  face_count: number;
}

export const DEFAULT_INSTRUMENTAL_SPECS: InstrumentalSpecs = {
  shoe_length_mm: 280,
  shoe_width_mm: 105,
  sole_thickness_mm: 30,
  arch_height_mm: 15,
  toe_spring_mm: 12,
  collar_height_mm: 55,
};

export const SPEC_CONSTRAINTS = {
  shoe_length_mm: { min: 250, max: 330, step: 1, label: 'Length (mm)' },
  shoe_width_mm: { min: 90, max: 130, step: 1, label: 'Width (mm)' },
  sole_thickness_mm: { min: 20, max: 45, step: 1, label: 'Sole Thickness (mm)' },
  arch_height_mm: { min: 5, max: 35, step: 1, label: 'Arch Height (mm)' },
  toe_spring_mm: { min: 5, max: 25, step: 1, label: 'Toe Spring (mm)' },
  collar_height_mm: { min: 30, max: 90, step: 1, label: 'Collar Height (mm)' },
} as const;
