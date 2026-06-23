"""
CI/CD pipeline validation tests (Phase 3B).
Tests GitHub Actions workflow, pre-commit hooks, deployment validation.
"""
from pathlib import Path

import pytest


def test_github_workflows_directory_exists():
    """Project has .github/workflows directory for CI/CD."""
    workflows_dir = Path(".github/workflows")
    assert workflows_dir.exists() and workflows_dir.is_dir()


def test_test_workflow_file_exists():
    """Test workflow exists for running tests and coverage."""
    workflow = Path(".github/workflows/test.yml")
    assert workflow.exists()


def test_test_workflow_runs_pytest():
    """Test workflow includes pytest command."""
    workflow = Path(".github/workflows/test.yml")
    content = workflow.read_text()

    assert "pytest" in content
    assert "coverage" in content.lower() or "cov" in content


def test_test_workflow_checks_coverage_gate():
    """Test workflow enforces 90% coverage minimum."""
    workflow = Path(".github/workflows/test.yml")
    content = workflow.read_text()

    assert "90" in content or "fail_under" in content


def test_lint_workflow_file_exists():
    """Lint workflow exists for code quality checks."""
    workflow = Path(".github/workflows/lint.yml")
    assert workflow.exists()


def test_lint_workflow_runs_ruff():
    """Lint workflow includes ruff for linting."""
    workflow = Path(".github/workflows/lint.yml")
    content = workflow.read_text()

    assert "ruff" in content


def test_lint_workflow_runs_type_check():
    """Lint workflow includes type checking (mypy or pyright)."""
    workflow = Path(".github/workflows/lint.yml")
    content = workflow.read_text()

    assert "mypy" in content or "pyright" in content or "type" in content.lower()


def test_precommit_config_exists():
    """Project has pre-commit configuration."""
    precommit = Path(".pre-commit-config.yaml")
    assert precommit.exists()


def test_precommit_includes_formatters():
    """Pre-commit config includes code formatters."""
    precommit = Path(".pre-commit-config.yaml")
    content = precommit.read_text()

    assert "black" in content or "format" in content.lower()


def test_precommit_includes_linters():
    """Pre-commit config includes linters."""
    precommit = Path(".pre-commit-config.yaml")
    content = precommit.read_text()

    assert "ruff" in content or "lint" in content.lower()


def test_precommit_includes_type_check():
    """Pre-commit config includes type checking."""
    precommit = Path(".pre-commit-config.yaml")
    content = precommit.read_text()

    assert "mypy" in content or "pyright" in content


def test_alembic_directory_exists():
    """Project has alembic migrations directory."""
    alembic_dir = Path("alembic")
    assert alembic_dir.exists() and alembic_dir.is_dir()


def test_alembic_env_py_exists():
    """Alembic env.py exists for migration configuration."""
    env_file = Path("alembic/env.py")
    assert env_file.exists()


def test_alembic_versions_directory_exists():
    """Alembic versions directory exists for migration files."""
    versions_dir = Path("alembic/versions")
    assert versions_dir.exists() and versions_dir.is_dir()


def test_alembic_ini_exists():
    """Alembic configuration file exists."""
    alembic_ini = Path("alembic.ini")
    assert alembic_ini.exists()


def test_alembic_ini_configured_for_postgres():
    """Alembic configured to use PostgreSQL."""
    alembic_ini = Path("alembic.ini")
    content = alembic_ini.read_text()

    assert "postgresql" in content or "postgres" in content


def test_migration_schema_initialization_exists():
    """Initial migration exists to create audit/HITL schema."""
    versions_dir = Path("alembic/versions")
    migrations = list(versions_dir.glob("*.py"))

    assert len(migrations) > 0, "No migrations found in alembic/versions/"
