"""seed software engineer KB

Revision ID: abec6df8c121
Revises: a6836919aecd
Create Date: 2025-09-09 21:16:10.139725

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'abec6df8c121'
down_revision: Union[str, Sequence[str], None] = 'a6836919aecd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Seed Software Engineer knowledge base entries."""
    kb = sa.table(
        'knowledge_base',
        sa.column('title', sa.String()),
        sa.column('content', sa.Text()),
        sa.column('category', sa.String()),
        sa.column('created_by', sa.String()),
        sa.column('is_active', sa.Boolean()),
    )

    rows = [
        {
            "title": "Clean Code Principles",
            "content": "Prefer meaningful names, small functions, single responsibility, and clear boundaries. Write tests.",
            "category": "software_engineering",
            "created_by": "seed",
            "is_active": True,
        },
        {
            "title": "Git Branching Strategy",
            "content": "Use main as release, develop for integration, feature/* branches, pull requests with review, squash merge.",
            "category": "software_engineering",
            "created_by": "seed",
            "is_active": True,
        },
        {
            "title": "PR Review Checklist",
            "content": "Compiles, tests pass, no secrets, clear naming, small diffs, docs updated, no dead code.",
            "category": "software_engineering",
            "created_by": "seed",
            "is_active": True,
        },
        {
            "title": "API Design Basics",
            "content": "Use nouns for resources, predictable paths, proper status codes, idempotency for PUT, pagination and filtering.",
            "category": "software_engineering",
            "created_by": "seed",
            "is_active": True,
        },
        {
            "title": "Python Project Structure",
            "content": "Use src/ layout or flat app/, type hints, linting, tests/, .env via dotenv, and pre-commit hooks.",
            "category": "software_engineering",
            "created_by": "seed",
            "is_active": True,
        },
    ]

    op.bulk_insert(kb, rows)


def downgrade() -> None:
    op.execute(
        "DELETE FROM knowledge_base WHERE created_by = 'seed' AND category = 'software_engineering'"
    )
