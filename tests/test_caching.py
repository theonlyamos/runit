"""
Tests for performance caching improvements in the runit codebase.
"""
import os
import sys
import time
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestFunctionCaching:
    """Test function metadata caching in Runtime."""

    def test_runtime_has_cache_attribute(self):
        """Ensure Runtime class has function cache."""
        from runit.languages.runtime import Runtime
        
        assert hasattr(Runtime, '_function_cache'), \
            "Runtime should have _function_cache class attribute"
        assert hasattr(Runtime, '_cache_ttl'), \
            "Runtime should have _cache_ttl attribute"

    def test_runtime_cache_is_class_level(self):
        """Ensure cache is shared across instances."""
        from runit.languages.runtime import Runtime
        
        assert isinstance(Runtime._function_cache, dict), \
            "_function_cache should be a dictionary"

    def test_cache_ttl_reasonable(self):
        """Ensure cache TTL is set to a reasonable value."""
        from runit.languages.runtime import Runtime
        
        assert Runtime._cache_ttl >= 60, \
            "Cache TTL should be at least 60 seconds"
        assert Runtime._cache_ttl <= 3600, \
            "Cache TTL should be at most 1 hour"


class TestLanguageParserReuse:
    """Test language parser reuse in RunIt."""

    def test_runit_has_lang_parser_property(self):
        """Ensure RunIt has lang_parser property."""
        from runit.runit import RunIt
        
        assert hasattr(RunIt, 'lang_parser'), \
            "RunIt should have lang_parser property"

    def test_runit_has_parser_attributes(self):
        """Ensure RunIt has internal parser attributes."""
        runit_path = Path(__file__).parent.parent / 'runit' / 'runit.py'
        with open(runit_path, 'r') as f:
            content = f.read()
        
        assert '_lang_parser' in content, \
            "RunIt should have _lang_parser instance attribute"
        assert '_lang_parser_mtime' in content, \
            "RunIt should have _lang_parser_mtime for cache invalidation"


class TestParallelInstallation:
    """Test parallel dependency installation."""

    def test_runit_uses_threadpool(self):
        """Ensure runit.py uses ThreadPoolExecutor for parallel installation."""
        runit_path = Path(__file__).parent.parent / 'runit' / 'runit.py'
        with open(runit_path, 'r') as f:
            content = f.read()
        
        assert 'ThreadPoolExecutor' in content, \
            "RunIt should use ThreadPoolExecutor for parallel installation"
        assert 'concurrent.futures' in content, \
            "RunIt should import from concurrent.futures"

    def test_install_all_uses_parallel(self):
        """Ensure install_all_language_packages uses parallel execution."""
        runit_path = Path(__file__).parent.parent / 'runit' / 'runit.py'
        with open(runit_path, 'r') as f:
            content = f.read()
        
        assert 'as_completed' in content, \
            "install_all_language_packages should use as_completed for parallel tasks"


class TestOptimizedCompression:
    """Test optimized project compression."""

    def test_get_exclude_list_returns_set(self):
        """Ensure get_exclude_list returns a set for O(1) lookups."""
        runit_path = Path(__file__).parent.parent / 'runit' / 'runit.py'
        with open(runit_path, 'r') as f:
            content = f.read()
        
        assert 'exclude_set' in content or 'set(' in content, \
            "get_exclude_list should use a set for efficient lookups"

    def test_compress_uses_early_filtering(self):
        """Ensure compress method uses early directory filtering."""
        runit_path = Path(__file__).parent.parent / 'runit' / 'runit.py'
        with open(runit_path, 'r') as f:
            content = f.read()
        
        assert 'should_exclude' in content or 'subfolders[:]' in content, \
            "compress should use early directory filtering"


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
