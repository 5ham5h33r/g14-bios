# Repository instructions

Read CONTRIBUTING.md before editing research or preparing a push.

This repository documents GA403WR BIOS releases from the 309 baseline onward, including 309 → 310 and 310 → 312. Maintain the release index and add a separate comparison for each future release, following docs/release-workflow.md. Keep existing comparisons and their evidence available.

Keep a `## Plain-language takeaway` section near the top of each release-comparison changelog. Before every push, update it to reflect the current findings. Explain the practical effect for a laptop owner and preserve uncertainty about untested behavior. Include a brief plain-language takeaway in the message reporting the push.

Write about the firmware and its behavior. Avoid first-person narration, including author diaries and repeated personal disclaimers. State testing status and specific gaps where they matter. Keep the main hardware limitations together in the coverage record. Do not replace a singular narrator with a collective narrator.

Keep writing direct and specific. Use the stop-slop skill when available. Avoid filler, promotional claims and em dashes. Preserve technical qualifications while removing repetitive prose.

Run `python tools/validate.py` before pushing. Run the relevant tool checks when changing analysis scripts.
