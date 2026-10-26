# Add a BIOS release

Track each upcoming GA403WR BIOS release against the preceding published version. Historical comparisons use the same process. Keep a separate changelog and evidence directory for each pair.

## Record the package

Check the [ASUS support page](https://www.asus.com/us/supportonly/ga403wr/helpdesk_bios/) for the complete GA403WR model. Record the official download URL, posting date, ZIP member name, ZIP hash and capsule hash in `data/releases.json`. Keep the firmware build date separate from the support-page date.

Add the verified release to the [release index](../changelog/README.md). If analysis is pending, say so. A version number or ASUS release note alone does not establish a code change.

## Compare the images

Follow the [comparison method](method.md). Reproduction guides cover [310 → 312](reproduce.md) and [309 → 310](reproduce-309-310.md). Check extraction offsets and layouts again for a new image before reusing them.

Store inventories and other evidence under `data/<old>-<new>/`. Put the detailed interpretation in pair-specific files under `research/`. Include coverage, tool failures and unresolved differences for that pair. Link existing code or upstream patches when they explain a change.

Use finding IDs within each comparison, such as `EC-01` or `LIB-01`. Keep the release-pair context in links so identical IDs on different pages remain distinct.

## Write the changelog

Copy the [template](changelog-template.md) into `changelog/<old>-to-<new>.md`. Lead with a plain-language takeaway: what changes for an owner, under which conditions, and what still needs testing. Follow with technical findings and evidence links.

Describe the firmware rather than the person examining it. Write “Hardware validation pending” or name the missing measurement. Avoid repeated author disclaimers, personal narration and guesses about performance.

Record unchanged components when the comparison establishes a match. Keep build dates, rebased addresses and other rebuild differences separate from behavior changes. Preserve qualifications such as the mode or call path where a change applies.

## Before each push

Update the takeaway, release index and README release table to match the findings. Check the writing against the rules in [CONTRIBUTING.md](../CONTRIBUTING.md).

Run `python tools/validate.py`. Run the relevant tool checks when analysis scripts change. Add checks for new evidence formats as needed; preserve the checks for earlier comparisons.

Keep firmware binaries and full disassembly in `local/`. Publish the evidence needed to check a finding, including hashes, module identities and short relevant excerpts.

For corrections, update the affected changelog and research notes together. Add a dated correction explaining what changed. A push report should link the updated page and give a brief plain-language takeaway.
