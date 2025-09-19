import glob
import os
from typing import Optional

from database import SessionLocal
from models import KnowledgeBase


def import_markdown_dir(directory: str, category: str, created_by: str = "import") -> int:
    session = SessionLocal()
    count = 0
    try:
        for path in glob.glob(os.path.join(directory, "**", "*.md"), recursive=True):
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            title = os.path.splitext(os.path.basename(path))[0]
            item = KnowledgeBase(
                title=title,
                content=content,
                category=category,
                created_by=created_by,
                is_active=True,
            )
            session.add(item)
            count += 1
        session.commit()
    finally:
        session.close()
    return count


def main() -> None:
    directory = os.environ.get("KB_MD_DIR", "kb_md")
    category = os.environ.get("KB_CATEGORY", "software_engineering")
    total = import_markdown_dir(directory, category)
    print(f"Imported {total} markdown files from {directory}")


if __name__ == "__main__":
    import os
    main()


