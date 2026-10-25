import importlib.util
from pathlib import Path
import struct
import unittest
import uuid

spec = importlib.util.spec_from_file_location("firmware", Path(__file__).resolve().parents[1] / "tools/firmware.py")
fw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fw)


class InputValidation(unittest.TestCase):
    def test_rejects_changed_download(self):
        with self.assertRaises(ValueError):
            fw.verified(b"changed", fw.sha256(b"original"))

    def test_rejects_zero_signature_size(self):
        record = uuid.UUID(int=0).bytes_le + struct.pack("<III", 28, 0, 0)
        with self.assertRaises(ValueError):
            fw.parse_signature_lists(record, authenticated=False)

    def test_rejects_signature_past_end(self):
        record = uuid.UUID(int=0).bytes_le + struct.pack("<III", 100, 0, 48)
        with self.assertRaises(ValueError):
            fw.parse_signature_lists(record, authenticated=False)

    def test_authentication_certificate_length_is_variable(self):
        kind = uuid.UUID("c1c41626-504c-4092-aca9-41f936934328")
        owner = uuid.UUID("26dc4851-195f-4ae1-9a19-fbf883bbb35e")
        auth = b"\0" * 16 + struct.pack("<I", 32) + b"\0" * 28
        esl = kind.bytes_le + struct.pack("<III", 76, 0, 48) + owner.bytes_le + b"\x42" * 32
        entries = fw.parse_signature_lists(auth + esl)
        self.assertEqual(entries, [{"type": str(kind), "owner": str(owner), "signature": "42" * 32}])


if __name__ == "__main__":
    unittest.main()
