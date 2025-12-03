import os
import tempfile
import pytest
import sys
from pathlib import Path


# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from msgspec_ext.fast_dotenv import parse_env_file, load_dotenv


class TestFileReading:
    """Test comprehensive file reading scenarios."""
    
    def test_empty_file(self):
        """Test parsing empty file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write("")
            f.flush()
            result = parse_env_file(f.name)
            assert result == {}
            Path(f.name).unlink()
    
    def test_whitespace_only_file(self):
        """Test file with only whitespace."""
        content = "   \n\t\n  \n"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write(content)
            f.flush()
            result = parse_env_file(f.name)
            assert result == {}
            Path(f.name).unlink()
    
    def test_comments_only_file(self):
        """Test file with only comments."""
        content = "# This is a comment\n# Another comment\n# Third comment"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write(content)
            f.flush()
            result = parse_env_file(f.name)
            assert result == {}
            Path(f.name).unlink()
    
    def test_mixed_whitespace_comments(self):
        """Test file with mixed whitespace and comments."""
        content = "# Comment 1\n   \n# Comment 2\n\t\n   # Comment 3"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write(content)
            f.flush()
            result = parse_env_file(f.name)
            assert result == {}
            Path(f.name).unlink()
    
    def test_file_with_bom(self):
        """Test file with UTF-8 BOM."""
        content = "VAR1=value1\nVAR2=value2"
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".env", delete=False) as f:
            f.write(b'\xef\xbb\xbf' + content.encode('utf-8'))
            f.flush()
            result = parse_env_file(f.name)
            assert result == {"VAR1": "value1", "VAR2": "value2"}
            Path(f.name).unlink()
    
    def test_very_long_lines(self):
        """Test file with very long lines."""
        long_value = "x" * 10000
        content = f"LONG_VAR={long_value}"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write(content)
            f.flush()
            result = parse_env_file(f.name)
            assert result["LONG_VAR"] == long_value
            assert len(result["LONG_VAR"]) == 10000
            Path(f.name).unlink()
    
    def test_very_long_variable_names(self):
        """Test file with very long variable names."""
        long_name = "X" * 1000
        content = f"{long_name}=value"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write(content)
            f.flush()
            result = parse_env_file(f.name)
            assert result[long_name] == "value"
            Path(f.name).unlink()
    
    def test_large_file_performance(self):
        """Test parsing large file with many variables."""
        # Create file with 1000 variables
        content = "\n".join([f"VAR_{i}=value_{i}" for i in range(1000)])
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write(content)
            f.flush()
            result = parse_env_file(f.name)
            assert len(result) == 1000
            assert result["VAR_0"] == "value_0"
            assert result["VAR_999"] == "value_999"
            Path(f.name).unlink()


class TestEncodingScenarios:
    """Test various encoding scenarios."""
    
    def test_utf8_encoding(self):
        """Test UTF-8 encoded files."""
        content = "UTF_VAR=value with unicode: café, naïve, 日本語"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", encoding="utf-8", delete=False) as f:
            f.write(content)
            f.flush()
            result = parse_env_file(f.name, encoding="utf-8")
            assert result["UTF_VAR"] == "value with unicode: café, naïve, 日本語"
            Path(f.name).unlink()
    
    def test_latin1_encoding(self):
        """Test Latin-1 encoded files."""
        content = "LATIN_VAR=value with accents: café, naïve"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", encoding="latin-1", delete=False) as f:
            f.write(content)
            f.flush()
            result = parse_env_file(f.name, encoding="latin-1")
            assert result["LATIN_VAR"] == "value with accents: café, naïve"
            Path(f.name).unlink()
    
    def test_different_encodings_same_content(self):
        """Test same content with different encodings."""
        content = "TEST_VAR=simple_value"
        
        # UTF-8
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", encoding="utf-8", delete=False) as f:
            f.write(content)
            f.flush()
            result_utf8 = parse_env_file(f.name, encoding="utf-8")
            Path(f.name).unlink()
        
        # Latin-1
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", encoding="latin-1", delete=False) as f:
            f.write(content)
            f.flush()
            result_latin = parse_env_file(f.name, encoding="latin-1")
            Path(f.name).unlink()
        
        assert result_utf8 == result_latin
    
    def test_encoding_with_special_chars(self):
        """Test encoding with special characters."""
        content = 'SPECIAL_VAR="value with emojis: 🚀 🎯 ⚡"'
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", encoding="utf-8", delete=False) as f:
            f.write(content)
            f.flush()
            result = parse_env_file(f.name, encoding="utf-8")
            assert result["SPECIAL_VAR"] == "value with emojis: 🚀 🎯 ⚡"
            Path(f.name).unlink()


class TestEdgeCases:
    """Test edge cases and corner scenarios."""
    
    def test_no_newline_at_end(self):
        """Test file without newline at end."""
        content = "VAR1=value1\nVAR2=value2"  # No final newline
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write(content)
            f.flush()
            result = parse_env_file(f.name)
            assert result == {"VAR1": "value1", "VAR2": "value2"}
            Path(f.name).unlink()
    
    def test_multiple_newlines(self):
        """Test file with multiple consecutive newlines."""
        content = "VAR1=value1\n\n\n\nVAR2=value2"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write(content)
            f.flush()
            result = parse_env_file(f.name)
            assert result == {"VAR1": "value1", "VAR2": "value2"}
            Path(f.name).unlink()
    
    def test_carriage_return_handling(self):
        """Test handling of carriage returns."""
        content = "VAR1=value1\r\nVAR2=value2\r\nVAR3=value3"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write(content)
            f.flush()
            result = parse_env_file(f.name)
            assert result == {"VAR1": "value1", "VAR2": "value2", "VAR3": "value3"}
            Path(f.name).unlink()
    
    def test_mixed_line_endings(self):
        """Test mixed line ending styles."""
        content = "VAR1=value1\nVAR2=value2\r\nVAR3=value3\nVAR4=value4\r\n"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write(content)
            f.flush()
            result = parse_env_file(f.name)
            assert result == {"VAR1": "value1", "VAR2": "value2", "VAR3": "value3", "VAR4": "value4"}
            Path(f.name).unlink()
    
    def test_trailing_whitespace(self):
        """Test handling of trailing whitespace."""
        content = "VAR1=value1   \nVAR2=value2\t\nVAR3=value3 \t"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write(content)
            f.flush()
            result = parse_env_file(f.name)
            assert result == {"VAR1": "value1", "VAR2": "value2", "VAR3": "value3"}
            Path(f.name).unlink()
    
    def test_leading_whitespace(self):
        """Test handling of leading whitespace."""
        content = "   VAR1=value1\n\tVAR2=value2\n VAR3=value3"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write(content)
            f.flush()
            result = parse_env_file(f.name)
            assert result == {"VAR1": "value1", "VAR2": "value2", "VAR3": "value3"}
            Path(f.name).unlink()


class TestQuoteHandling:
    """Test comprehensive quote handling scenarios."""
    
    def test_single_quotes(self):
        """Test single quoted values."""
        content = "VAR1='value1'\nVAR2='value with spaces'\nVAR3='value with = equals'"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write(content)
            f.flush()
            result = parse_env_file(f.name)
            assert result["VAR1"] == "value1"
            assert result["VAR2"] == "value with spaces"
            assert result["VAR3"] == "value with = equals"
            Path(f.name).unlink()
    
    def test_double_quotes(self):
        """Test double quoted values."""
        content = 'VAR1="value1"\nVAR2="value with spaces"\nVAR3="value with = equals"'
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write(content)
            f.flush()
            result = parse_env_file(f.name)
            assert result["VAR1"] == "value1"
            assert result["VAR2"] == "value with spaces"
            assert result["VAR3"] == "value with = equals"
            Path(f.name).unlink()
    
    def test_mixed_quotes(self):
        """Test mixed quote styles."""
        content = 'VAR1="double quoted"\nVAR2=\'single quoted\'\nVAR3=unquoted'
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write(content)
            f.flush()
            result = parse_env_file(f.name)
            assert result["VAR1"] == "double quoted"
            assert result["VAR2"] == "single quoted"
            assert result["VAR3"] == "unquoted"
            Path(f.name).unlink()
    
    def test_escaped_quotes_double(self):
        """Test escaped quotes in double quoted values."""
        content = 'VAR1="value with \\"escaped\\" quotes"\nVAR2="normal value"'
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write(content)
            f.flush()
            result = parse_env_file(f.name)
            assert result["VAR1"] == 'value with "escaped" quotes'
            assert result["VAR2"] == "normal value"
            Path(f.name).unlink()
    
    def test_escaped_quotes_single(self):
        """Test escaped quotes in single quoted values."""
        content = "VAR1='value with \\\'escaped\\\' quotes'\nVAR2='normal value'"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write(content)
            f.flush()
            result = parse_env_file(f.name)
            assert result["VAR1"] == "value with 'escaped' quotes"
            assert result["VAR2"] == "normal value"
            Path(f.name).unlink()
    
    def test_nested_quotes(self):
        """Test nested quote scenarios."""
        content = 'VAR1="value with \'nested\' quotes"\nVAR2=\'value with "nested" quotes\''
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write(content)
            f.flush()
            result = parse_env_file(f.name)
            assert result["VAR1"] == "value with 'nested' quotes"
            assert result["VAR2"] == 'value with "nested" quotes'
            Path(f.name).unlink()
    
    def test_incomplete_quotes(self):
        """Test incomplete quote handling."""
        content = 'VAR1="incomplete quote\nVAR2=normal_value\nVAR3=\'another incomplete'
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write(content)
            f.flush()
            result = parse_env_file(f.name)
            # Should handle gracefully - implementation specific
            assert "VAR2" in result
            assert result["VAR2"] == "normal_value"
            Path(f.name).unlink()
    
    def test_empty_quoted_values(self):
        """Test empty quoted values."""
        content = 'VAR1=""\nVAR2=\'\'\nVAR3=""\nVAR4=\'\''
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write(content)
            f.flush()
            result = parse_env_file(f.name)
            assert result["VAR1"] == ""
            assert result["VAR2"] == ""
            assert result["VAR3"] == ""
            assert result["VAR4"] == ""
            Path(f.name).unlink()
    
    def test_quotes_with_special_chars(self):
        """Test quotes containing special characters."""
        content = 'VAR1="value with $pecial@Chars#"\nVAR2="value with = equals"\nVAR3="value with : colon"'
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write(content)
            f.flush()
            result = parse_env_file(f.name)
            assert result["VAR1"] == "value with $pecial@Chars#"
            assert result["VAR2"] == "value with = equals"
            assert result["VAR3"] == "value with : colon"
            Path(f.name).unlink()


class TestSpecialValues:
    """Test special value scenarios."""
    
    def test_values_with_equals(self):
        """Test values containing equals signs."""
        content = "VAR1=key=value\nVAR2=equation=x+y=z\nVAR3=url=https://example.com?param=value"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write(content)
            f.flush()
            result = parse_env_file(f.name)
            assert result["VAR1"] == "key=value"
            assert result["VAR2"] == "equation=x+y=z"
            assert result["VAR3"] == "url=https://example.com?param=value"
            Path(f.name).unlink()
    
    def test_values_with_spaces(self):
        """Test values with various spacing."""
        content = "VAR1=value with spaces\nVAR2=  leading spaces\nVAR3=trailing spaces  \nVAR4=  both spaces  "
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write(content)
            f.flush()
            result = parse_env_file(f.name)
            assert result["VAR1"] == "value with spaces"
            # Preserves spaces in unquoted values ​​(removes trailing only).
            assert result["VAR2"] == "  leading spaces"  # preserves leading spaces
            assert result["VAR3"] == "trailing spaces"  # remove trailing spaces
            assert result["VAR4"] == "  both spaces"  # removes trailing but preserves leading
            Path(f.name).unlink()
    
    def test_values_with_newlines(self):
        """Test quoted values containing newlines."""
        content = 'VAR1="line1\\nline2\\nline3"\nVAR2="single line"'
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write(content)
            f.flush()
            result = parse_env_file(f.name)
            assert result["VAR1"] == "line1\nline2\nline3"
            assert result["VAR2"] == "single line"
            Path(f.name).unlink()
    
    def test_values_with_tabs(self):
        """Test values containing tab characters."""
        # Using real-world content with escape sequences
        content = 'VAR1="value\twith\ttabs"\nVAR2=normal_value'
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write(content)
            f.flush()
            result = parse_env_file(f.name)
            assert result["VAR1"] == "value\twith\ttabs"
            assert result["VAR2"] == "normal_value"
            Path(f.name).unlink()
    
    def test_zero_values(self):
        """Test numeric zero values."""
        content = "VAR1=0\nVAR2=0.0\nVAR3=0000\nVAR4=-0"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write(content)
            f.flush()
            result = parse_env_file(f.name)
            assert result["VAR1"] == "0"
            assert result["VAR2"] == "0.0"
            assert result["VAR3"] == "0000"
            assert result["VAR4"] == "-0"
            Path(f.name).unlink()
    
    def test_boolean_like_values(self):
        """Test boolean-like string values."""
        content = "VAR1=true\nVAR2=false\nVAR3=True\nVAR4=False\nVAR5=TRUE\nVAR6=FALSE"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write(content)
            f.flush()
            result = parse_env_file(f.name)
            assert result["VAR1"] == "true"
            assert result["VAR2"] == "false"
            assert result["VAR3"] == "True"
            assert result["VAR4"] == "False"
            assert result["VAR5"] == "TRUE"
            assert result["VAR6"] == "FALSE"
            Path(f.name).unlink()
    
    def test_special_symbols(self):
        """Test values with special symbols."""
        # Starts comment on unquoted values
        content = "VAR1=!@#$%^&*()\nVAR2=<>?:\"{}|\\\\\nVAR3=[];',./\nVAR4=±§©®™"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", encoding="utf-8", delete=False) as f:
            f.write(content)
            f.flush()
            result = parse_env_file(f.name)
            # treats # as the beginning of a comment in unquoted values
            assert result["VAR1"] == "!@"  # Everything after # is a comment
            assert result["VAR2"] == "<>?:\"{}|\\\\"  # Without #, it preserves everything
            assert result["VAR3"] == "[];',./"
            assert result["VAR4"] == "±§©®™"
            Path(f.name).unlink()


class TestVariableNames:
    """Test variable name validation and handling."""
    
    def test_valid_variable_names(self):
        """Test various valid variable name formats."""
        content = """
SIMPLE_VAR=value1
_with_underscore=value2
WITH123NUMBERS=value3
MixedCase_VAR=value4
VAR_WITH_UNDERSCORES=value5
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write(content)
            f.flush()
            result = parse_env_file(f.name)
            expected = {
                "SIMPLE_VAR": "value1",
                "_with_underscore": "value2", 
                "WITH123NUMBERS": "value3",
                "MixedCase_VAR": "value4",
                "VAR_WITH_UNDERSCORES": "value5"
            }
            assert result == expected
            Path(f.name).unlink()
    
    def test_invalid_variable_names(self):
        """Test handling of invalid variable names."""
        content = """
123INVALID=start_with_number
invalid-dash=has_dash
invalid.dot=has_dot
invalid space=has_space
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write(content)
            f.flush()
            result = parse_env_file(f.name)
            # Should skip invalid names, only export pattern might work
            assert len(result) <= 1  # At most the export pattern
            Path(f.name).unlink()
    
    def test_export_pattern(self):
        """Test export keyword patterns."""
        content = """
export VAR1=value1
export    VAR2=value2
export	VAR3=value3
export VAR4="quoted value"
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write(content)
            f.flush()
            result = parse_env_file(f.name)
            assert result["VAR1"] == "value1"
            assert result["VAR2"] == "value2"
            assert result["VAR3"] == "value3"
            assert result["VAR4"] == "quoted value"
            Path(f.name).unlink()
    
    def test_case_sensitivity(self):
        """Test case sensitivity in variable names."""
        content = """
var_lower=value1
VAR_UPPER=value2
Var_Mixed=value3
var_lower_duplicate=value4
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write(content)
            f.flush()
            result = parse_env_file(f.name)
            # All should be preserved as separate variables
            assert "var_lower" in result
            assert "VAR_UPPER" in result
            assert "Var_Mixed" in result
            # V7 comportamento: dict naturalmente sobrescreve duplicatas
            assert result["var_lower"] == "value1"  # Primeiro valor lido
            # var_lower_duplicate é uma variável diferente de var_lower
            assert result["var_lower_duplicate"] == "value4"
            Path(f.name).unlink()


class TestErrorHandling:
    """Test error handling and edge error cases."""
    
    def test_nonexistent_file(self):
        """Test handling of non-existent file."""
        result = parse_env_file("nonexistent_file.env")
        assert result == {}
    
    def test_file_permission_error(self):
        """Test file permission errors."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write("VAR1=value1")
            f.flush()
            # Make file unreadable (Unix-like systems)
            try:
                os.chmod(f.name, 0o000)
                result = parse_env_file(f.name)
                # Should handle gracefully
                assert result == {} or "VAR1" in result
            except OSError:
                # Permission error expected on some systems
                pass
            finally:
                # Restore permissions for cleanup
                try:
                    os.chmod(f.name, 0o644)
                except OSError:
                    pass
                Path(f.name).unlink()
    
    def test_directory_instead_of_file(self):
        """Test when path is a directory instead of file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = parse_env_file(temp_dir)
            assert result == {}
    
    def test_binary_file_handling(self):
        """Test handling of binary/non-text files."""
        # Create a file with binary content
        binary_content = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".env", delete=False) as f:
            f.write(binary_content)
            f.flush()
            result = parse_env_file(f.name)
            # Should handle gracefully
            assert isinstance(result, dict)
            Path(f.name).unlink()
    
    def test_symlink_handling(self):
        """Test handling of symbolic links."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write("VAR1=value1")
            f.flush()
            
            # Create symlink
            symlink_path = f.name + ".symlink"
            try:
                os.symlink(f.name, symlink_path)
                result = parse_env_file(symlink_path)
                assert result["VAR1"] == "value1"
            except OSError:
                # Symlinks not supported on all systems
                pass
            finally:
                try:
                    Path(symlink_path).unlink()
                except OSError:
                    pass
                Path(f.name).unlink()
    
    def test_malformed_lines(self):
        """Test handling of malformed lines."""
        content = """
VALID_VAR=valid_value
INVALID_LINE_NO_EQUALS
=invalid_start_with_equals
VALID_VAR_2=another_value
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write(content)
            f.flush()
            result = parse_env_file(f.name)
            # Should parse valid lines and skip invalid ones
            assert "VALID_VAR" in result
            assert result["VALID_VAR"] == "valid_value"
            assert "VALID_VAR_2" in result
            assert result["VALID_VAR_2"] == "another_value"
            # Invalid lines should be skipped
            assert len(result) == 2
            Path(f.name).unlink()


class TestLoadingFunction:
    """Test the load_dotenv function comprehensively."""
    
    def test_load_env_basic(self):
        """Test basic loading functionality."""
        content = "TEST_LOAD_VAR=test_value"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write(content)
            f.flush()
            
            # Clear any existing env var
            if "TEST_LOAD_VAR" in os.environ:
                del os.environ["TEST_LOAD_VAR"]
            
            result = load_dotenv(f.name)
            assert result is True
            assert os.environ.get("TEST_LOAD_VAR") == "test_value"
            
            # Cleanup
            if "TEST_LOAD_VAR" in os.environ:
                del os.environ["TEST_LOAD_VAR"]
            Path(f.name).unlink()
    
    def test_load_env_no_override(self):
        """Test that existing environment variables are not overridden."""
        content = "EXISTING_VAR=new_value"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write(content)
            f.flush()
            
            # Set existing environment variable
            original_value = "original_value"
            os.environ["EXISTING_VAR"] = original_value
            
            result = load_dotenv(f.name)
            assert result is True
            # Should not override existing variable
            assert os.environ.get("EXISTING_VAR") == original_value
            
            # Cleanup
            del os.environ["EXISTING_VAR"]
            Path(f.name).unlink()
    
    def test_load_env_override(self):
        """Test override functionality."""
        content = "OVERRIDE_VAR=new_value"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write(content)
            f.flush()
            
            # Set existing environment variable
            os.environ["OVERRIDE_VAR"] = "original_value"
            
            result = load_dotenv(f.name, override=True)
            assert result is True
            # Should override existing variable
            assert os.environ.get("OVERRIDE_VAR") == "new_value"
            
            # Cleanup
            del os.environ["OVERRIDE_VAR"]
            Path(f.name).unlink()
    
    def test_load_env_empty_file(self):
        """Test loading empty file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write("")
            f.flush()
            
            result = load_dotenv(f.name)
            assert result is False  # Empty file should return False
            
            Path(f.name).unlink()
    
    def test_load_env_nonexistent_file(self):
        """Test loading non-existent file."""
        result = load_dotenv("nonexistent_file.env")
        assert result is False
    
    def test_load_env_multiple_variables(self):
        """Test loading multiple variables."""
        content = """
VAR_1=value1
VAR_2=value2
VAR_3=value3
VAR_4=value4
VAR_5=value5
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write(content)
            f.flush()
            
            # Clear any existing vars
            for i in range(1, 6):
                var_name = f"VAR_{i}"
                if var_name in os.environ:
                    del os.environ[var_name]
            
            result = load_dotenv(f.name)
            assert result is True
            
            # Verify all variables were loaded
            for i in range(1, 6):
                var_name = f"VAR_{i}"
                assert os.environ.get(var_name) == f"value{i}"
            
            # Cleanup
            for i in range(1, 6):
                var_name = f"VAR_{i}"
                if var_name in os.environ:
                    del os.environ[var_name]
            
            Path(f.name).unlink()
    
    def test_load_env_with_special_chars(self):
        """Test loading variables with special characters."""
        content = """
SPECIAL_VAR="quoted value with spaces"
SYMBOLS_VAR="!@#$%^&*()"
URL_VAR=https://example.com/path?param=value
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write(content)
            f.flush()
            
            # Clear existing
            for var in ["SPECIAL_VAR", "SYMBOLS_VAR", "URL_VAR"]:
                if var in os.environ:
                    del os.environ[var]
            
            result = load_dotenv(f.name)
            assert result is True
            
            assert os.environ.get("SPECIAL_VAR") == "quoted value with spaces"
            assert os.environ.get("SYMBOLS_VAR") == "!@#$%^&*()"
            assert os.environ.get("URL_VAR") == "https://example.com/path?param=value"
            
            # Cleanup
            for var in ["SPECIAL_VAR", "SYMBOLS_VAR", "URL_VAR"]:
                if var in os.environ:
                    del os.environ[var]
            
            Path(f.name).unlink()


class TestRealWorldScenarios:
    """Test real-world scenarios and common use cases."""
    
    def test_typical_web_app_env(self):
        """Test typical web application .env file."""
        content = """
# Database Configuration
DATABASE_URL=postgresql://user:pass@localhost:5432/myapp
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=myapp
DATABASE_USER=appuser
DATABASE_PASSWORD="secure_password123!"

# Application Settings
APP_NAME="My Web App"
APP_ENV=production
APP_DEBUG=false
APP_PORT=8000
APP_HOST=0.0.0.0

# API Keys
API_KEY="sk-1234567890abcdef"
SECRET_KEY="super-secret-key-for-jwt-tokens"

# External Services
REDIS_URL=redis://localhost:6379/0
CACHE_DRIVER=redis
MAIL_DRIVER=smtp
MAIL_HOST=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME="app@example.com"
MAIL_PASSWORD="app-specific-password"

# Feature Flags
FEATURE_NEW_UI=true
FEATURE_BETA_API=false
FEATURE_ANALYTICS=true

# URLs
APP_URL=https://myapp.com
API_URL=https://api.myapp.com
CDN_URL=https://cdn.myapp.com
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write(content)
            f.flush()
            result = parse_env_file(f.name)
            
            # Verify key configurations
            assert result["DATABASE_URL"] == "postgresql://user:pass@localhost:5432/myapp"
            assert result["APP_NAME"] == "My Web App"
            assert result["APP_DEBUG"] == "false"
            assert result["API_KEY"] == "sk-1234567890abcdef"
            assert result["FEATURE_NEW_UI"] == "true"
            assert result["APP_URL"] == "https://myapp.com"
            
            Path(f.name).unlink()
    
    def test_docker_compose_env(self):
        """Test Docker Compose style environment file."""
        content = """
# Docker Compose Environment
COMPOSE_PROJECT_NAME=myproject
COMPOSE_FILE=docker-compose.yml:docker-compose.prod.yml

# Database
MYSQL_ROOT_PASSWORD="root-password-with-special-chars!"
MYSQL_DATABASE=myapp
MYSQL_USER=appuser
MYSQL_PASSWORD="user-password-123"

# Application
APP_ENV=production
APP_PORT=8080
APP_HOST=0.0.0.0

# Volumes
DATA_VOLUME_PATH=/var/lib/docker/volumes/myproject_data
LOGS_VOLUME_PATH=/var/log/myproject

# Networks
NETWORK_DRIVER=bridge
NETWORK_SUBNET=172.20.0.0/16
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write(content)
            f.flush()
            result = parse_env_file(f.name)
            
            assert result["COMPOSE_PROJECT_NAME"] == "myproject"
            assert result["MYSQL_ROOT_PASSWORD"] == "root-password-with-special-chars!"
            assert result["MYSQL_DATABASE"] == "myapp"
            assert result["APP_PORT"] == "8080"
            assert result["DATA_VOLUME_PATH"] == "/var/lib/docker/volumes/myproject_data"
            
            Path(f.name).unlink()
    
    def test_microservices_env(self):
        """Test microservices environment configuration."""
        content = """
# Service Discovery
CONSUL_HOST=consul.service.consul
CONSUL_PORT=8500
CONSUL_TOKEN="consul-acl-token"

# Message Queue
RABBITMQ_HOST=rabbitmq.service.consul
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD="guest-password"
RABBITMQ_VHOST="/"

# Service URLs
USER_SERVICE_URL=http://user-service:8080
ORDER_SERVICE_URL=http://order-service:8080
PAYMENT_SERVICE_URL=http://payment-service:8080

# Circuit Breaker
CIRCUIT_BREAKER_THRESHOLD=5
CIRCUIT_BREAKER_TIMEOUT=30
CIRCUIT_BREAKER_ENABLED=true

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
RATE_LIMIT_ENABLED=true

# Tracing
JAEGER_AGENT_HOST=jaeger-agent
JAEGER_AGENT_PORT=6831
JAEGER_SAMPLER_TYPE=const
JAEGER_SAMPLER_PARAM=1
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write(content)
            f.flush()
            result = parse_env_file(f.name)
            
            assert result["CONSUL_HOST"] == "consul.service.consul"
            assert result["RABBITMQ_PASSWORD"] == "guest-password"
            assert result["USER_SERVICE_URL"] == "http://user-service:8080"
            assert result["CIRCUIT_BREAKER_THRESHOLD"] == "5"
            assert result["RATE_LIMIT_REQUESTS"] == "100"
            assert result["JAEGER_SAMPLER_PARAM"] == "1"
            
            Path(f.name).unlink()
    
    def test_development_env(self):
        """Test development environment configuration."""
        content = """
# Development Environment
NODE_ENV=development
DEBUG=true
VERBOSE=true

# Local Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=dev_db
DB_USER=dev_user
DB_PASSWORD="dev-password"

# Local Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Local Services
API_BASE_URL=http://localhost:3000
WEBSOCKET_URL=ws://localhost:3001
STATIC_URL=http://localhost:3002

# Development Tools
HOT_RELOAD=true
SOURCE_MAPS=true
LINT_ON_SAVE=true

# Testing
TEST_DATABASE_NAME=test_db
TEST_API_KEY="test-api-key-123"
MOCK_EXTERNAL_SERVICES=true
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write(content)
            f.flush()
            result = parse_env_file(f.name)
            
            assert result["NODE_ENV"] == "development"
            assert result["DEBUG"] == "true"
            assert result["DB_HOST"] == "localhost"
            assert result["DB_PASSWORD"] == "dev-password"
            assert result["API_BASE_URL"] == "http://localhost:3000"
            assert result["HOT_RELOAD"] == "true"
            assert result["TEST_API_KEY"] == "test-api-key-123"
            
            Path(f.name).unlink()

class TestPerformanceStress:
    """Stress tests for performance validation."""
    
    def test_massive_file_parsing(self):
        """Test parsing massive file with 10,000 variables."""
        # This tests memory efficiency and parsing speed
        content = "\n".join([f"VAR_{i}=value_{i}" for i in range(10000)])
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write(content)
            f.flush()
            
            result = parse_env_file(f.name)
            assert len(result) == 10000
            assert result["VAR_0"] == "value_0"
            assert result["VAR_9999"] == "value_9999"
            assert result["VAR_5000"] == "value_5000"
            
            Path(f.name).unlink()
    
    def test_deeply_nested_quotes(self):
        """Test deeply nested quote scenarios."""
        content = 'VAR1="level1 \\"level2 \\"level3\\" back2\\" back1"'
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write(content)
            f.flush()
            result = parse_env_file(f.name)
            assert result["VAR1"] == 'level1 "level2 \"level3\" back2" back1'
            Path(f.name).unlink()
    
    def test_extremely_long_quoted_value(self):
        """Test extremely long quoted value."""
        long_text = "x" * 50000
        content = f'LONG_VAR="{long_text}"'
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write(content)
            f.flush()
            result = parse_env_file(f.name)
            assert result["LONG_VAR"] == long_text
            assert len(result["LONG_VAR"]) == 50000
            Path(f.name).unlink()
    
    def test_unicode_mixed_encodings(self):
        """Test mixed Unicode scenarios."""
        content = """
ENGLISH=Hello World
CHINESE=你好世界
JAPANESE=こんにちは世界
ARABIC=مرحبا بالعالم
RUSSIAN=Привет мир
EMOJIS=🚀 🎯 ⚡ 🔥 💪
MATH_SYMBOLS=∑ ∏ ∫ ∂ ∇
CURRENCY=$ € £ ¥ ₹
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", encoding="utf-8", delete=False) as f:
            f.write(content)
            f.flush()
            result = parse_env_file(f.name, encoding="utf-8")
            
            assert result["ENGLISH"] == "Hello World"
            assert result["CHINESE"] == "你好世界"
            assert result["JAPANESE"] == "こんにちは世界"
            assert result["ARABIC"] == "مرحبا بالعالم"
            assert result["RUSSIAN"] == "Привет мир"
            assert result["EMOJIS"] == "🚀 🎯 ⚡ 🔥 💪"
            assert result["MATH_SYMBOLS"] == "∑ ∏ ∫ ∂ ∇"
            assert result["CURRENCY"] == "$ € £ ¥ ₹"
            
            Path(f.name).unlink()


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])
