import os
import re
import subprocess
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

        # Store source directory path for later use (e.g., static folder copying)
        self.source_dir = root.resolve()

        merged_content = self._compile_course(root)

        # Debug mode: write merged content to disk
        debug_mode = os.getenv("MU_DEBUG_FOLDER_MD", "0") == "1"

        # Create a temp file with merged content and pass to parent Reader
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as tmp:
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

    @staticmethod
    def _rewrite_image_paths(body: str, unit_path: Path, root: Path) -> str:
        """
        Rewrite image paths to be relative to course root.

        All images must be in <course_root>/static/.
        Any path like ../../static/foo.webp becomes /static/foo.webp
        Subdirectory structure is preserved (e.g., /static/diagrams/img.webp)
        """

        def rewrite_match(match):
            alt_text = match.group(1)
            img_path = match.group(2)

            # Skip external URLs
            if img_path.startswith(("http://", "https://")):
                return match.group(0)  # Return unchanged

            # Extract the path components
            path_obj = Path(img_path)

            # Check if path contains 'static' directory
            parts = path_obj.parts
            if "static" in parts:
                # Find static and preserve everything after it
                static_idx = parts.index("static")
                # Reconstruct path from static onwards with / prefix (absolute from root)
                new_path = "/static"
                if len(parts) > static_idx + 1:
                    # Join remaining parts with forward slashes
                    new_path = new_path + "/" + "/".join(parts[static_idx + 1 :])
            else:
                # No static in path - extract just the filename
                # This will be validated later and may warn
                new_path = "/static/" + path_obj.name

            # Validate file exists in static folder
            static_file = root / "static"
            if "static" in parts and len(parts) > static_idx + 1:
                static_file = static_file.joinpath(*parts[static_idx + 1 :])
            else:
                static_file = static_file / path_obj.name
            
            if not static_file.exists():
                print(
                    f"[WARNING] Image not found: {static_file} (referenced in {unit_path})"
                )

            # Return rewritten markdown
            return f"![{alt_text}]({new_path})"

        # Match markdown image syntax: ![alt text](path)
        pattern = r"!\[([^\]]*)\]\(([^)]+)\)"
        return re.sub(pattern, rewrite_match, body)

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
            print(
                f"[WARNING] Course index.md has uncommented text body, ignoring it: {index_path}"
            )

        title = fm.get("title", "Untitled Course")
        organization = fm.get("organization", "org")
        course_number = fm.get("course_number", "course")
        course_run = fm.get("course_run", "course")
        
        # Read additional course metadata
        description = fm.get("description", "")
        course_image = fm.get("course_image", "")
        video_embed = fm.get("video_embed", "")
        start_date = fm.get("start_date", "")
        end_date = fm.get("end_date", "")
        enrollment_start = fm.get("enrollment_start", "")
        enrollment_end = fm.get("enrollment_end", "")
        effort = fm.get("effort", "")
        duration = fm.get("duration", "")
        language = fm.get("language", "")
        
        # Read overview from separate file if exists
        overview = ""
        overview_path = root / "overview.md"
        if overview_path.exists():
            overview_fm, overview_body = self._read_md(overview_path)
            # Convert markdown to HTML for OLX
            try:
                overview_html = subprocess.check_output(
                    ["pandoc", "--from=markdown", "--to=html5"],
                    input=overview_body.strip().encode(),
                ).decode()
                overview = overview_html.strip()
            except (FileNotFoundError, subprocess.CalledProcessError) as e:
                print(f"[WARNING] Could not convert overview.md to HTML: {e}")
                overview = overview_body.strip()

        # Build attributes string for markdown header
        attrs = [
            f"olx-org={organization}",
            f"olx-course={course_number}",
            f"olx-url_name={course_run}",
        ]
        if description:
            # Escape quotes and special characters for attribute value
            description_escaped = description.replace('"', '&quot;')
            attrs.append(f'course-description="{description_escaped}"')
        if course_image:
            attrs.append(f'course-image="{course_image}"')
        if video_embed:
            # Escape quotes and special characters for attribute value
            video_escaped = video_embed.replace('"', '&quot;')
            attrs.append(f'course-video="{video_escaped}"')
        if start_date:
            attrs.append(f'course-start-date="{start_date}"')
        if end_date:
            attrs.append(f'course-end-date="{end_date}"')
        if enrollment_start:
            attrs.append(f'course-enrollment-start="{enrollment_start}"')
        if enrollment_end:
            attrs.append(f'course-enrollment-end="{enrollment_end}"')
        if effort:
            effort_escaped = effort.replace('"', '&quot;')
            attrs.append(f'course-effort="{effort_escaped}"')
        if duration:
            duration_escaped = duration.replace('"', '&quot;')
            attrs.append(f'course-duration="{duration_escaped}"')
        if language:
            attrs.append(f'course-language="{language}"')
        if overview:
            # Escape and encode overview
            overview_escaped = overview.replace('"', '&quot;').replace('\n', '&#10;')
            attrs.append(f'course-overview="{overview_escaped}"')

        output.append(f"# {title} {{{' '.join(attrs)}}}")
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
                print(
                    f"[WARNING] Chapter index.md has uncommented text body, ignoring it: {chapter_index}"
                )

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
                    print(
                        f"[WARNING] Sequential index.md has uncommented text body, ignoring it: {seq_index}"
                    )

                output.append(self._heading(3, fm.get("title", sequential.name)))
                output.append("")

                # ================ UNITS ================
                units = self._sorted_items(
                    [
                        p
                        for p in sequential.iterdir()
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

                    # Rewrite image paths before appending body
                    body = self._rewrite_image_paths(body, unit, root)

                    output.append(body.rstrip())
                    output.append("")

        return "\n".join(output).strip() + "\n"
