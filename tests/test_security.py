"""
Tests for security improvements in the runit codebase.
"""
import os
import sys
import ast
import subprocess
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestEvalReplacement:
    """Test that eval() has been replaced with safe parsing."""

    def test_runtime_uses_ast_literal_eval(self):
        """Ensure runtime.py uses ast.literal_eval instead of eval()."""
        runtime_path = Path(__file__).parent.parent / 'runit' / 'languages' / 'runtime.py'
        with open(runtime_path, 'r') as f:
            content = f.read()
        
        # Check that standalone eval() is not used (not literal_eval)
        import re
        standalone_eval = re.search(r'(?<!literal_)eval\s*\(', content)
        assert standalone_eval is None, "runtime.py should not use standalone eval()"
        assert 'ast.literal_eval' in content, "runtime.py should use ast.literal_eval"

    def test_multi_uses_ast_literal_eval(self):
        """Ensure multi.py uses ast.literal_eval instead of eval()."""
        multi_path = Path(__file__).parent.parent / 'runit' / 'languages' / 'multi.py'
        with open(multi_path, 'r') as f:
            content = f.read()
        
        # Check that standalone eval() is not used (not literal_eval)
        import re
        standalone_eval = re.search(r'(?<!literal_)eval\s*\(', content)
        assert standalone_eval is None, "multi.py should not use standalone eval()"
        assert 'ast.literal_eval' in content or 'json.loads' in content, \
            "multi.py should use ast.literal_eval or json.loads"

    def test_ast_literal_eval_safe(self):
        """Test that ast.literal_eval safely parses without executing code."""
        safe_dict = "{'key': 'value', 'number': 42}"
        result = ast.literal_eval(safe_dict)
        assert result == {'key': 'value', 'number': 42}

    def test_ast_literal_eval_rejects_malicious_input(self):
        """Test that ast.literal_eval rejects malicious code."""
        malicious = "__import__('os').system('echo pwned')"
        with pytest.raises((ValueError, SyntaxError)):
            ast.literal_eval(malicious)


class TestShellInjectionPrevention:
    """Test that shell injection vulnerabilities are fixed."""

    def test_runtime_uses_subprocess_run(self):
        """Ensure runtime.py uses subprocess.run instead of shell=True."""
        runtime_path = Path(__file__).parent.parent / 'runit' / 'languages' / 'runtime.py'
        with open(runtime_path, 'r') as f:
            content = f.read()
        
        assert 'shell=True' not in content, "runtime.py should not use shell=True"
        assert 'subprocess.run' in content, "runtime.py should use subprocess.run"

    def test_multi_uses_subprocess_run(self):
        """Ensure multi.py uses subprocess.run instead of shell=True."""
        multi_path = Path(__file__).parent.parent / 'runit' / 'languages' / 'multi.py'
        with open(multi_path, 'r') as f:
            content = f.read()
        
        assert 'shell=True' not in content, "multi.py should not use shell=True"
        assert 'subprocess.run' in content, "multi.py should use subprocess.run"

    def test_subprocess_with_list_args(self):
        """Test that subprocess.run with list args prevents injection."""
        result = subprocess.run(
            ['echo', 'hello; rm -rf /'],
            capture_output=True,
            text=True
        )
        assert 'hello; rm -rf /' in result.stdout


class TestTokenStorage:
    """Test secure token storage."""

    def test_account_uses_keyring(self):
        """Ensure account.py uses keyring for token storage."""
        account_path = Path(__file__).parent.parent / 'runit' / 'modules' / 'account.py'
        with open(account_path, 'r') as f:
            content = f.read()
        
        assert 'import keyring' in content, "account.py should import keyring"
        assert 'shelve' not in content, "account.py should not use shelve"

    @patch('keyring.get_password')
    def test_load_token_retrieves_token(self, mock_get_password):
        """Test that load_token retrieves token from keyring."""
        mock_get_password.return_value = 'test_token_123'
        
        from runit.modules.account import load_token
        result = load_token()
        
        assert result == 'test_token_123'
        mock_get_password.assert_called_once()

    @patch('keyring.set_password')
    def test_load_token_stores_token(self, mock_set_password):
        """Test that load_token stores token in keyring."""
        from runit.modules.account import load_token
        load_token('new_token_456')
        
        mock_set_password.assert_called_once()


class TestInputValidation:
    """Test input validation improvements."""

    def test_account_update_project_validates_input(self):
        """Test that update_project validates key=value format."""
        account_path = Path(__file__).parent.parent / 'runit' / 'modules' / 'account.py'
        with open(account_path, 'r') as f:
            content = f.read()
        
        assert "split('=', 1)" in content or 'split("=", 1)' in content, \
            "account.py should use maxsplit=1 for key=value parsing"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
