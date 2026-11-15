import { Html, OrbitControls } from '@react-three/drei'
import { Canvas } from '@react-three/fiber'
import { Suspense } from 'react'
import type { CatalogItem } from '../../data/catalog'
import { MeshBoundary } from './Furniture'
import { FurnitureMesh } from './FurnitureMesh'

/** One on-demand canvas for the selected model, rather than a WebGL context per card. */
export function CatalogPreview({ item }: { item: CatalogItem }) {
  const size = Math.max(
    item.bbox_m.width,
    item.bbox_m.height,
    item.bbox_m.depth,
  )
  return (
    <figure className="shrink-0 rounded-[2px] border border-hairline-ink bg-paper-card/65">
      <div
        role="img"
        aria-label={`3D preview of ${item.name}`}
        className="h-40"
      >
        <Canvas
          frameloop="demand"
          dpr={[1, 1.5]}
          camera={{ position: [1.7, 1.2, 2], fov: 40 }}
          fallback={
            <p className="p-3 text-[12px] text-ink-medium">
              3D preview unavailable. You can still add the model.
            </p>
          }
        >
          <ambientLight intensity={1.6} />
          <directionalLight position={[3, 5, 4]} intensity={1.4} />
          <MeshBoundary
            key={item.glb_url}
            fallback={
              <Html center>
                <p
                  role="status"
                  className="w-48 text-center text-[12px] text-ink-medium"
                >
                  Model preview unavailable. Check the reconstruction service.
                </p>
              </Html>
            }
          >
            <Suspense
              fallback={
                <Html center>
                  <p
                    role="status"
                    className="whitespace-nowrap text-[12px] text-ink-medium"
                  >
                    Loading model…
                  </p>
                </Html>
              }
            >
              <group
                scale={1 / size}
                position={[0, -item.bbox_m.height / size / 2, 0]}
              >
                <FurnitureMesh item={item} play={false} />
              </group>
            </Suspense>
          </MeshBoundary>
          <OrbitControls enablePan={false} enableZoom={false} />
        </Canvas>
      </div>
      <figcaption className="border-t border-hairline-ink px-3 py-2">
        <p className="truncate text-[12px] font-medium">{item.name}</p>
        <p className="text-[10px] text-ink-mist">Drag to rotate preview</p>
      </figcaption>
    </figure>
  )
}
