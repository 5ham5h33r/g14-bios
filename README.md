# G14 BIOS notes

Firmware changes for the **2025 ASUS ROG Zephyrus G14, GA403WR**.

ASUS describes BIOS 312 as “Optimize system performance.” I wanted to know what changed, so I started comparing the update images. These notes cover the code, tables and bundled firmware I can identify, with offsets and hashes for checking the findings.

**Start with the [plain-language takeaway for 310 → 312](changelog/310-to-312.md#plain-language-takeaway).** The detailed evidence follows it. The comparison covers:

| Area | Finding |
|---|---|
| Embedded controller | 03.10F → 03.12F; changes to battery-care charging and charger communication |
| Secure Boot | 59 added hashes in the default revocation list |
| Wi-Fi | One MediaTek 6 GHz country-policy bit |
| UEFI libraries | Changes matching two OpenSSL security fixes |
| BIOS setup | Function-level comparison in the research notes |

I label a result **confirmed** when I can point to the bytes or instructions. I use **inferred** when I can explain the code but still need a hardware test or a vendor definition. Unresolved changes keep their offsets so someone else can pick up the work.

## Research

- [Detailed changelog](changelog/310-to-312.md)
- [EC charging and hardware-control notes](research/310-312-ec.md)
- [UEFI and upstream security patches](research/310-312-uefi.md)
- [Coverage and open questions](research/coverage.md)
- [Method and address conventions](docs/method.md)
- [Reproduce the comparison](docs/reproduce.md)
- [Firmware hashes and source URLs](data/releases.json)

The initial comparison uses ASUS's published 310 and 312 EZ Flash packages. It does not use a flash-chip dump from a specific laptop. I have not tested 312 on hardware as part of this research.

## Scope

GA403WR has its own firmware. A version number shared with a GA403UV, GA403WW or another G14 does not make the images interchangeable. Check your complete model before using any download from ASUS.

I keep ASUS binaries and full decompiler output outside Git. This repository contains research, hashes, small instruction excerpts and the tools to repeat the work. Download the firmware from the [ASUS support page](https://www.asus.com/us/supportonly/ga403wr/helpdesk_bios/).

## Contributing

An offset, a before/after measurement or a correction helps more than a general stability report. [CONTRIBUTING.md](CONTRIBUTING.md) describes the evidence to include. Open an issue if you can explain an unresolved routine or test one of the inferred effects.

## License

I license the original notes and scripts under [MIT](LICENSE). ASUS firmware and upstream code retain their respective licenses. This is an independent project; ASUS has not endorsed it.
