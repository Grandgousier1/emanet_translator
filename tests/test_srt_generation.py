import sys
import types
from pathlib import Path

# Ensure the project root is on the Python path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Stub external dependencies if they are not installed
for name in ["yt_dlp", "whisper"]:
    if name not in sys.modules:
        sys.modules[name] = types.ModuleType(name)

if "torch" not in sys.modules:
    torch_stub = types.ModuleType("torch")
    class DummyCuda:
        @staticmethod
        def is_available():
            return False
    torch_stub.cuda = DummyCuda()
    def device(name):
        return name
    torch_stub.device = device
    sys.modules["torch"] = torch_stub

if "transformers" not in sys.modules:
    transformers_stub = types.ModuleType("transformers")
    class AutoTokenizer:
        @classmethod
        def from_pretrained(cls, *args, **kwargs):
            return cls()
    class AutoModelForSeq2SeqLM:
        @classmethod
        def from_pretrained(cls, *args, **kwargs):
            return cls()
    transformers_stub.AutoTokenizer = AutoTokenizer
    transformers_stub.AutoModelForSeq2SeqLM = AutoModelForSeq2SeqLM
    sys.modules["transformers"] = transformers_stub

if "srt" not in sys.modules:
    srt_stub = types.ModuleType("srt")
    class Subtitle:
        def __init__(self, index, start, end, content):
            self.index = index
            self.start = start
            self.end = end
            self.content = content
    def compose(subs):
        def fmt(td):
            total_ms = int(td.total_seconds() * 1000)
            hours = total_ms // 3600000
            minutes = (total_ms % 3600000) // 60000
            seconds = (total_ms % 60000) // 1000
            ms = total_ms % 1000
            return f"{hours:02}:{minutes:02}:{seconds:02},{ms:03}"
        lines = []
        for s in subs:
            lines.append(str(s.index))
            lines.append(f"{fmt(s.start)} --> {fmt(s.end)}")
            lines.append(s.content)
            lines.append("")
        return "\n".join(lines)
    srt_stub.Subtitle = Subtitle
    srt_stub.compose = compose
    sys.modules["srt"] = srt_stub

from emanet_translator import EmanetTranslator


def test_create_srt_file(tmp_path: Path):
    translator = EmanetTranslator()
    translator.output_dir = tmp_path

    segments = [
        {"start": 0, "end": 1, "text": "Bonjour"},
        {"start": 1, "end": 2, "text": "Au revoir"},
    ]

    output_path = translator.create_srt_file(segments, "sample.srt")

    assert output_path.exists()
    content = output_path.read_text(encoding="utf-8")

    assert "00:00:00,000 --> 00:00:01,000" in content
    assert "Bonjour" in content
    assert "Au revoir" in content

    output_path.unlink()
