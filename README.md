# G14 BIOS changelog

Detailed changelogs for the **2025 ASUS ROG Zephyrus G14, GA403WR**, covering BIOS 309 → 310, 310 → 312 and future releases.

ASUS's release note for 312 says “Optimize system performance.” Each comparison here documents the changes in the published firmware: code, configuration tables, bundled components and security updates. Findings include hashes and offsets so others can check the evidence.

## Release history

| BIOS comparison | ASUS posting date | Main changes |
|---|---|---|
| [310 → 312](changelog/310-to-312.md) | October 21, 2026 | Battery-care charging, power settings after unplugging, Secure Boot revocations and OpenSSL patch matches |
| [309 → 310](changelog/309-to-310.md) | July 22, 2026 | AMD platform firmware, CPU-core controls, GPU power ordering, graphics-memory request encoding, USB4 polling and memory handling |

Each comparison starts with a plain-language takeaway: [310 → 312](changelog/310-to-312.md#plain-language-takeaway) or [309 → 310](changelog/309-to-310.md#plain-language-takeaway). The technical findings follow it.

New releases get a comparison against the preceding published version, a plain-language takeaway and supporting research. The [release index](changelog/README.md) tracks coverage; the [release workflow](docs/release-workflow.md) covers how to add the next update. BIOS 309 is the earliest covered baseline.

## Evidence and testing

**Confirmed** findings point to bytes or instructions. **Inferred** effects need a hardware test or a vendor definition. Unresolved changes retain their offsets and open questions.

The comparisons use ASUS's public EZ Flash packages. Hardware validation remains pending. See coverage and open questions for [310 → 312](research/coverage.md) and [309 → 310](research/309-310-coverage.md).

- [EC charging and power-control changes](research/310-312-ec.md)
- [UEFI changes and upstream security patches](research/310-312-uefi.md)
- [309 → 310 ACPI and GPU power transitions](research/309-310-acpi.md)
- [309 → 310 CPU controls, USB4 and AMD firmware](research/309-310-uefi.md)
- [309 → 310 EC metadata and relocation review](research/309-310-ec.md)
- [Method and address conventions](docs/method.md)
- [Reproduce the initial comparison](docs/reproduce.md)
- [Reproduce the 309 → 310 comparison](docs/reproduce-309-310.md)
- [Firmware hashes and official downloads](data/releases.json)

## Device scope

GA403WR has its own firmware. Shared version numbers across G14 models do not make their images interchangeable. Check your complete model on the [ASUS support page](https://www.asus.com/us/supportonly/ga403wr/helpdesk_bios/).

The repository contains research, hashes, short instruction excerpts and reproduction tools. Keep ASUS binaries and full decompiler output in the ignored `local/` directory.

## Contributing

Corrections, explanations of unresolved routines and repeatable hardware measurements are welcome. Include the model, BIOS versions and supporting evidence. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

Original notes and scripts use the [MIT license](LICENSE). ASUS firmware and upstream code retain their respective licenses. This project has no affiliation with ASUS.
