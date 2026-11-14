// Shared contract types. contracts/schema.py is the source of truth; schema.ts mirrors it.
export type {
  AuditReport,
  BBoxM,
  CollisionPart,
  DoorOpening,
  FurnitureItem,
  LayoutProposal,
  OptimiseRequest,
  Pose2D,
  RoomScene,
  Vec2,
  WallSegment,
  WindowOpening,
} from '../../../contracts/schema'
export {
  MIN_HEIGHT_OVERLAP_M,
  WALK_HEADROOM_M,
} from '../../../contracts/schema'
