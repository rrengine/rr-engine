/**
 * 3D Shoe Viewer Component
 *
 * Renders GLB shoe models using React Three Fiber.
 * Supports orbit controls, lighting, and model loading.
 */

import { Suspense, useRef } from 'react';
import { Canvas, useFrame, useLoader } from '@react-three/fiber';
import { OrbitControls, Environment, Center, Html, useProgress } from '@react-three/drei';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import * as THREE from 'three';

interface ShoeModelProps {
  url: string;
  autoRotate?: boolean;
}

function Loader() {
  const { progress } = useProgress();
  return (
    <Html center>
      <div className="flex flex-col items-center gap-2">
        <div className="w-32 h-2 bg-gray-700 rounded-full overflow-hidden">
          <div
            className="h-full bg-blue-500 transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
        <span className="text-sm text-gray-400">{progress.toFixed(0)}%</span>
      </div>
    </Html>
  );
}

function ShoeModel({ url, autoRotate = true }: ShoeModelProps) {
  const gltf = useLoader(GLTFLoader, url);
  const meshRef = useRef<THREE.Group>(null);

  useFrame((_, delta) => {
    if (autoRotate && meshRef.current) {
      meshRef.current.rotation.y += delta * 0.3;
    }
  });

  return (
    <Center>
      <group ref={meshRef}>
        <primitive object={gltf.scene} scale={0.01} />
      </group>
    </Center>
  );
}

function PlaceholderShoe() {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame((_, delta) => {
    if (meshRef.current) {
      meshRef.current.rotation.y += delta * 0.3;
    }
  });

  return (
    <mesh ref={meshRef}>
      <boxGeometry args={[2, 0.5, 1]} />
      <meshStandardMaterial color="#444" wireframe />
    </mesh>
  );
}

interface ShoeViewerProps {
  modelUrl?: string | null;
  autoRotate?: boolean;
  className?: string;
}

export function ShoeViewer({ modelUrl, autoRotate = true, className = '' }: ShoeViewerProps) {
  return (
    <div className={`w-full h-full min-h-[400px] bg-gray-900 rounded-lg overflow-hidden ${className}`}>
      <Canvas
        camera={{ position: [5, 3, 5], fov: 45 }}
        gl={{ antialias: true, alpha: true }}
      >
        <color attach="background" args={['#111']} />

        {/* Lighting */}
        <ambientLight intensity={0.4} />
        <directionalLight position={[10, 10, 5]} intensity={1} castShadow />
        <directionalLight position={[-10, 5, -5]} intensity={0.5} />
        <pointLight position={[0, 10, 0]} intensity={0.5} />

        {/* Environment for reflections */}
        <Environment preset="studio" />

        {/* Model */}
        <Suspense fallback={<Loader />}>
          {modelUrl ? (
            <ShoeModel url={modelUrl} autoRotate={autoRotate} />
          ) : (
            <PlaceholderShoe />
          )}
        </Suspense>

        {/* Controls */}
        <OrbitControls
          enablePan={true}
          enableZoom={true}
          enableRotate={true}
          minDistance={2}
          maxDistance={20}
          autoRotate={false}
        />

        {/* Grid */}
        <gridHelper args={[10, 10, '#333', '#222']} position={[0, -1, 0]} />
      </Canvas>
    </div>
  );
}

export default ShoeViewer;
