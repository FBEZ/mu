import os
import tempfile
import yaml
from pathlib import Path
from typing import Tuple, Dict, Any, List

from mu.formats.md.reader import Reader as SingleFileReader
from mu.exceptions import MuError


class Reader(SingleFileReader):
    """
    Reads a folder structure of Markdown files and merges them into a single course.
    
    Expected folder structure:
    course_folder/
    ├── index.md (course metadata and description)
    ├── chapter1/
    │   ├── index.md (chapter metadata)
    │   ├── sequential1/
    │   │   ├── index.md (sequential metadata)
    │   │   ├── unit1.md
    │   │   └── unit2.md
    │   └── sequential2/
    │       └── ...
    └── chapter2/
        └── ...
    
    Debug mode:
    Set MU_DEBUG_FOLDER_MD=1 environment variable to write merged markdown to disk.
    """

    def __init__(self, folder_path: str) -> None:
        root = Path(folder_path)
        if not root.is_dir():
            raise MuError(f"Folder path does not exist: {folder_path}")
        
        merged_content = self._compile_course(root)
        
        # Debug mode: write merged content to disk
        debug_mode = os.getenv("MU_DEBUG_FOLDER_MD", "0") == "1"
        
        # Create a temp file with merged content and pass to parent Reader
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as tmp:
            tmp.write(merged_content)
            tmp.flush()
            temp_path = tmp.name
        
        try:
            super().__init__(temp_path)
        finally:
            # Clean up temp file after reading (unless debug mode)
            if not debug_mode:
                Path(temp_path).unlink()
            else:
                print(f"[DEBUG] Temp file kept at: {temp_path}")

    @staticmethod
    def _read_md(path: Path) -> Tuple[Dict[str, Any], str]:
        """
        Read a markdown file and extract frontmatter and body.
        Returns a tuple of (frontmatter_dict, body_text).
        """
        text = path.read_text(encoding="utf-8")

        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                fm = yaml.safe_load(parts[1]) or {}
                body = parts[2].lstrip()
                return fm, body

        return {}, text

    @staticmethod
    def _is_hidden(frontmatter: Dict[str, Any]) -> bool:
        """Check if file is marked as hidden or draft."""
        return frontmatter.get("hidden") or frontmatter.get("draft")

    @staticmethod
    def _has_uncommented_text(body: str) -> bool:
        """Check if body contains uncommented text (not just HTML comments)."""
        # Remove all HTML comments
        text = body
        while "<!--" in text:
            start = text.find("<!--")
            end = text.find("-->", start)
            if end == -1:
                end = len(text)
            else:
                end += 3
            text = text[:start] + text[end:]
        
        # Check if remaining text is non-empty (ignoring whitespace)
        return bool(text.strip())

    @staticmethod
    def _sorted_items(items: List[Path]) -> List[Path]:
        """Sort items by frontmatter 'order' field, then by name."""
        def sort_key(p: Path):
            if p.suffix == ".md":
                fm, _ = Reader._read_md(p)
                return (fm.get("order", 9999), p.name)
            return (9999, p.name)

        return sorted(items, key=sort_key)

    @staticmethod
    def _heading(level: int, title: str) -> str:
        """Generate markdown heading."""
        return f"{'#' * level} {title}"

    def _compile_course(self, root: Path) -> str:
        """
        Recursively compile course structure from folder hierarchy.
        Generates merged markdown with proper hierarchy.
        """
        output = []

        # ================ COURSE ================
        index_path = root / "index.md"
        if not index_path.exists():
            raise MuError(f"Course index.md not found at {index_path}")

        fm, body = self._read_md(index_path)

        # Warn if course index.md has uncommented text
        if self._has_uncommented_text(body):
            print(f"[WARNING] Course index.md has uncommented text body, ignoring it: {index_path}")

        title = fm.get("title", "Untitled Course")
        org = fm.get("org", "org")
        course = fm.get("course", "course")
        url_name = fm.get("url_name", "course")

        output.append(
            f"# {title} {{olx-org={org} olx-course={course} olx-url_name={url_name}}}"
        )
        output.append("")

        # ================ CHAPTERS ================
        chapters = self._sorted_items([p for p in root.iterdir() if p.is_dir()])

        for chapter in chapters:
            chapter_index = chapter / "index.md"
            if not chapter_index.exists():
                continue

            fm, body = self._read_md(chapter_index)
            if self._is_hidden(fm):
                continue

            # Warn if chapter index.md has uncommented text
            if self._has_uncommented_text(body):
                print(f"[WARNING] Chapter index.md has uncommented text body, ignoring it: {chapter_index}")

            output.append(self._heading(2, fm.get("title", chapter.name)))
            output.append("")

            # ================ SEQUENTIALS ================
            sequentials = self._sorted_items(
                [p for p in chapter.iterdir() if p.is_dir()]
            )

            for sequential in sequentials:
                seq_index = sequential / "index.md"
                if not seq_index.exists():
                    continue

                fm, body = self._read_md(seq_index)
                if self._is_hidden(fm):
                    continue

                # Warn if sequential index.md has uncommented text
                if self._has_uncommented_text(body):
                    print(f"[WARNING] Sequential index.md has uncommented text body, ignoring it: {seq_index}")

                output.append(self._heading(3, fm.get("title", sequential.name)))
                output.append("")

                # ================ UNITS ================
                units = self._sorted_items(
                    [
                        p for p in sequential.iterdir()
                        if p.suffix == ".md" and p.name != "index.md"
                    ]
                )

                for unit in units:
                    fm, body = self._read_md(unit)
                    if self._is_hidden(fm):
                        continue

                    title = fm.get("title")
                    if title:
                        output.append(self._heading(4, title))
                        output.append("")

                    output.append(body.rstrip())
                    output.append("")

        return "\n".join(output).strip() + "\n"