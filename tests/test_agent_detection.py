"""Tests for agent detection functionality."""

from mcp.types import Implementation, InitializeRequestParams
from src.mcp_server_guide.agent_detection import AGENT_PREFIX_MAP, AgentInfo, detect_agent, normalize_agent_name


def test_agent_info_creation():
    """Test AgentInfo dataclass creation."""
    info = AgentInfo(name="test-client", normalized_name="test", version="1.0.0", prompt_prefix="@")
    assert info.name == "test-client"
    assert info.normalized_name == "test"
    assert info.version == "1.0.0"
    assert info.prompt_prefix == "@"


def test_normalize_kiro():
    """Test normalization of Kiro/Amazon Q agents."""
    assert normalize_agent_name("kiro-cli") == "kiro"
    assert normalize_agent_name("amazon-q") == "kiro"
    assert normalize_agent_name("KIRO-CLI") == "kiro"
    assert normalize_agent_name("Q DEV CLI") == "kiro"
    assert normalize_agent_name("q dev cli") == "kiro"


def test_normalize_claude():
    """Test normalization of Claude agents."""
    assert normalize_agent_name("claude-desktop") == "claude"
    assert normalize_agent_name("claude-code") == "claude"
    assert normalize_agent_name("Claude") == "claude"


def test_normalize_cursor():
    """Test normalization of Cursor agents."""
    assert normalize_agent_name("cursor") == "cursor"
    assert normalize_agent_name("cursor-agent") == "cursor"
    assert normalize_agent_name("CURSOR") == "cursor"


def test_normalize_copilot():
    """Test normalization of Copilot agents."""
    assert normalize_agent_name("github-copilot") == "copilot"
    assert normalize_agent_name("copilot") == "copilot"


def test_normalize_gemini():
    """Test normalization of Gemini agents."""
    assert normalize_agent_name("gemini-cli") == "gemini"
    assert normalize_agent_name("gemini") == "gemini"


def test_normalize_windsurf():
    """Test normalization of Windsurf agents."""
    assert normalize_agent_name("windsurf") == "windsurf"


def test_normalize_unknown():
    """Test normalization of unknown agents."""
    assert normalize_agent_name("unknown-client") == "unknown"
    assert normalize_agent_name("some-random-agent") == "unknown"


def test_prefix_mapping():
    """Test agent prefix mapping."""
    assert AGENT_PREFIX_MAP["kiro"] == "@"
    assert AGENT_PREFIX_MAP["claude"] == "/{mcp_name}:"
    assert AGENT_PREFIX_MAP["cursor"] == "@"
    assert AGENT_PREFIX_MAP["copilot"] == "/"
    assert AGENT_PREFIX_MAP["gemini"] == "@"
    assert AGENT_PREFIX_MAP["windsurf"] == "/"


def test_detect_agent_kiro():
    """Test agent detection for Kiro."""
    params = InitializeRequestParams(
        protocolVersion="1.0", capabilities={}, clientInfo=Implementation(name="kiro-cli", version="1.0.0")
    )

    info = detect_agent(params)
    assert info.name == "kiro-cli"
    assert info.normalized_name == "kiro"
    assert info.version == "1.0.0"
    assert info.prompt_prefix == "@"


def test_detect_agent_claude():
    """Test agent detection for Claude."""
    params = InitializeRequestParams(
        protocolVersion="1.0", capabilities={}, clientInfo=Implementation(name="claude-desktop", version="2.0.0")
    )

    info = detect_agent(params)
    assert info.name == "claude-desktop"
    assert info.normalized_name == "claude"
    assert info.version == "2.0.0"
    assert info.prompt_prefix == "/{mcp_name}:"


def test_detect_agent_unknown():
    """Test agent detection for unknown agent."""
    params = InitializeRequestParams(
        protocolVersion="1.0", capabilities={}, clientInfo=Implementation(name="unknown-agent", version="1.0.0")
    )

    info = detect_agent(params)
    assert info.name == "unknown-agent"
    assert info.normalized_name == "unknown"
    assert info.version == "1.0.0"
    assert info.prompt_prefix == "/"  # Default fallback
