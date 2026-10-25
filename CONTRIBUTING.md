# Contributing

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
