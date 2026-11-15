"""Session-wide test settings."""

import os
import tempfile

# The reconstruction app mounts its furniture file store at import. Point it at a throwaway
# directory, always (never a developer's real pipeline data), so tests can write and wipe it.
os.environ["FURNITURE_DATA_DIR"] = tempfile.mkdtemp(prefix="spaceshift-test-furniture-")
