import importlib.util
from pathlib import Path
import struct
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("acpi_tables", Path(__file__).resolve().parents[1] / "tools/acpi_tables.py")
acpi = importlib.util.module_from_spec(spec)
spec.loader.exec_module(acpi)


def table(payload=b"\0"):
    data = bytearray(36) + payload
    data[:4] = b"SSDT"
    struct.pack_into("<I", data, 4, len(data))
    data[9] = -sum(data) % 256
    return bytes(data)


class AcpiTests(unittest.TestCase):
    def test_table_bounds_and_checksum(self):
        self.assertEqual(acpi.table_metadata(table())["bytes"], 37)
        self.assertIsNone(acpi.table_metadata(table()[:-1]))
        self.assertEqual(acpi.table_metadata(table() + b"extra"), acpi.table_metadata(table()))
        damaged = bytearray(table()); damaged[-1] ^= 1
        self.assertIsNone(acpi.table_metadata(damaged))
        short_header = bytearray(table()); struct.pack_into("<I", short_header, 4, 35)
        self.assertIsNone(acpi.table_metadata(short_header))

    def test_multiple_raw_sections_keep_identity(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            rows = []
            for i, payload in enumerate((b"A", b"B")):
                directory = root / f"{i} Raw section"; directory.mkdir()
                (directory / "body.bin").write_bytes(table(payload))
                rows.append({"display_path": directory.name, "key": f"file/Section:Raw#{i}"})
            result = acpi.scan(root, rows, "test")
            self.assertEqual(len(result), 2)
            changed = [dict(row) for row in result]
            changed[0]["sha256"] = "changed"
            self.assertEqual(len(acpi.compare(result, changed)), 1)
            self.assertEqual(acpi.compare(result, changed)[0]["key"], rows[0]["key"])

    def test_duplicate_keys_and_path_escape_rejected(self):
        row = {"key": "same", "sha256": "a"}
        with self.assertRaises(ValueError):
            acpi.compare([row, row], [])
        with tempfile.TemporaryDirectory() as name:
            with self.assertRaises(ValueError):
                acpi.scan(Path(name), [{"display_path": "../outside", "key": "x"}], "test")
