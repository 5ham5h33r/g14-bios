# Contributing

The goal is to document GA403WR BIOS changes across releases, starting with 310 → 312. Use the [release workflow](docs/release-workflow.md) for each upcoming version. Keep the [release index](changelog/README.md) current and preserve the evidence for earlier comparisons.

Keep code observations separate from hardware results. A change in a charging routine does not establish the behavior of a custom charge limit on a running laptop.

For a firmware finding, include:

- Full model, both BIOS versions and capsule SHA-256 hashes.
- Module GUID and instance, or an absolute capsule-file offset for the EC.
- The old and new instructions, enough surrounding code to explain the branch, and your interpretation.
- Tool versions and any loader options that affect the result.

For a hardware result, record the power source, performance mode, GPU mode, driver versions and relevant settings. Describe a repeatable procedure. Include the same measurements before and after the update if you have them.

Use the confidence labels in [the method](docs/method.md). A match to an upstream patch supports the patch's presence; reachability and exploitability need separate evidence.

Please leave firmware images, flash dumps, serial numbers, device identifiers and credentials out of issues and pull requests. Link the official download and include its hash. Small instruction excerpts and original pseudocode are enough for most findings.

Write changes in plain language. Name the condition and the resulting behavior. Keep speculation in the open-questions section and cite the source of a register or structure definition.

Every release-comparison changelog must start with a `## Plain-language takeaway` section before its technical findings. Explain what an owner might notice, define unfamiliar terms, and distinguish confirmed changes from effects that still need a hardware test. Keep addresses, instruction names and register details in the evidence sections. Update the takeaway whenever a finding changes, and check it before each push.

Describe the change without personal narration. Use specific evidence and short testing-status statements. Keep shared hardware-testing limits in the coverage notes; name a local uncertainty beside the finding it qualifies. Avoid repeated disclaimers and stock conclusions. A confident tone must still reflect the strength of the evidence.
