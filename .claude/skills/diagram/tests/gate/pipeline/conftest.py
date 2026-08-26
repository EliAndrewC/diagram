"""Fixtures the tests moved into this tree still take from their source module (feature 133 T29). A conftest is
where pytest looks for them, and here the name shadows nothing."""

from tests.pipeline.test_gencache import clean_gatehit  # noqa: F401
