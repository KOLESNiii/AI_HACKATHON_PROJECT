import { Line } from '@react-three/drei'
import { useEffect, useMemo } from 'react'
import { BufferGeometry, DoubleSide, Float32BufferAttribute } from 'three'
import type { DoorOpening, WallSegment } from '../../lib/contracts'
import { doorSwing, type Pt } from '../../lib/geometry'

const Y = 0.008

/** Floor area swept by one door leaf: an ochre wash, the ink arc and the open leaf. */
function DoorSwing({ fan }: { fan: Pt[] }) {
  const geometry = useMemo(() => {
    const [h, ...arc] = fan
    const pos: number[] = []
    for (let i = 0; i < arc.length - 1; i++)
      pos.push(
        h.x,
        Y,
        h.z,
        arc[i].x,
        Y,
        arc[i].z,
        arc[i + 1].x,
        Y,
        arc[i + 1].z,
      )
    const g = new BufferGeometry()
    g.setAttribute('position', new Float32BufferAttribute(pos, 3))
    return g
  }, [fan])
  useEffect(() => () => geometry.dispose(), [geometry])

  const [h, ...arc] = fan
  const at = (p: Pt) => [p.x, Y + 0.002, p.z] as [number, number, number]
  return (
    <group>
      <mesh geometry={geometry} raycast={() => null}>
        <meshBasicMaterial
          color="#a67c52"
          transparent
          opacity={0.22}
          side={DoubleSide}
          depthWrite={false}
        />
      </mesh>
      <Line
        points={arc.map(at)}
        color="#1c1a17"
        lineWidth={1.25}
        dashed
        dashSize={0.06}
        gapSize={0.04}
        transparent
        opacity={0.7}
      />
      <Line
        points={[at(h), at(arc[arc.length - 1])]}
        color="#1c1a17"
        lineWidth={1.75}
        transparent
        opacity={0.8}
      />
    </group>
  )
}

/** Swing areas for every hinged door; doors that don't swing draw nothing. */
export function DoorSwings({
  doors,
  walls,
}: {
  doors: DoorOpening[]
  walls: WallSegment[]
}) {
  const fans = useMemo(
    () =>
      doors.flatMap((d) => {
        const fan = doorSwing(d, walls)
        return fan ? [{ id: d.id, fan }] : []
      }),
    [doors, walls],
  )
  return (
    <>
      {fans.map(({ id, fan }) => (
        <DoorSwing key={id} fan={fan} />
      ))}
    </>
  )
}
