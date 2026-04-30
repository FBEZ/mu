import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from mu.formats.html.writer import Writer as HtmlWriter


class Writer(HtmlWriter):
    """
    Same as HTML writer, except that we convert the output to Markdown.
    """

    def write_to(self, path: str, source_dir: Optional[Path] = None) -> None:
        # Write html to temporary file
        with tempfile.NamedTemporaryFile("w") as of:
            super().write_to(of.name, source_dir=source_dir)
            of.flush()
            # Convert file with pandoc
            subprocess.check_call(
                ["pandoc", "--from=html", "--to=markdown", of.name, f"--output={path}"]
            )
