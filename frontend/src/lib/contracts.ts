// Shared contract types. contracts/schema.py is the source of truth; schema.ts mirrors it.
export type {
  AuditReport,
  BlockedDoorIssue,
  BBoxM,
  ChatReply,
  ChatRequest,
  ChatStreamEvent,
  DoorOpening,
  FengShuiRequest,
  FengShuiScore,
  FurnitureItem,
  LayoutGoal,
  LayoutProposal,
  LayoutProgress,
  LayoutStreamEvent,
  OptimiseRequest,
  Pose2D,
  ProductOption,
  RoomScene,
  Vec2,
  WallSegment,
} from '../../../contracts/schema'
export { MAX_LAYOUT_INSTRUCTION_CHARS } from '../../../contracts/schema'
