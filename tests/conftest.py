"""Session-wide test settings."""

import os
import tempfile

# The reconstruction app mounts its furniture file store at import. Point it at a throwaway
# directory, always (never a developer's real pipeline data), so tests can write and wipe it.
os.environ["FURNITURE_DATA_DIR"] = tempfile.mkdtemp(prefix="spaceshift-test-furniture-")
# Likewise the demo cache (#20): tests that use one point at it explicitly, so an empty room
# stays empty unless a test says otherwise.
os.environ["FURNITURE_DEMO_CACHE_DIR"] = tempfile.mkdtemp(prefix="spaceshift-test-demo-cache-")
# And the scene cache (#12): no plan is known until a test uploads or restores one.
os.environ["SCENE_DEMO_CACHE_DIR"] = tempfile.mkdtemp(prefix="spaceshift-test-scene-cache-")
