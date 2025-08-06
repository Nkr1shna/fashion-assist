# Development Rules & Guidelines

## Python Package Management Rule

### Rule: Always Use `uv add` Instead of `pip install`
### Rule: Always use .venv in the project instead of $HOME/.local/bin/env

**🚫 DON'T USE:**
```bash
pip install package_name
pip3 install package_name
pip install --break-system-packages package_name
python -m pip install package_name
```

**✅ USE INSTEAD:**
```bash
uv add package_name
```

### Why This Rule Exists

1. **Speed**: uv is 10-100x faster than pip
2. **Better Dependency Resolution**: More reliable conflict resolution
3. **Modern Python Project Management**: Built for modern Python workflows
4. **Security**: Better verification and validation of packages
5. **Consistency**: Ensures reproducible environments across all developers

### Implementation Guidelines

#### For New Dependencies
```bash
# Add production dependencies
uv add streamlit torch transformers requests beautifulsoup4

# Add development dependencies  
uv add --dev pytest black flake8 mypy

# Add optional dependencies
uv add --optional gui tkinter
```

#### For Running Scripts
```bash
# Instead of: python script.py
uv run python script.py

# Instead of: python -m module
uv run python -m module

# For Streamlit apps
uv run streamlit run app.py

# ⚠️ IMPORTANT: Never use global environments
# ❌ DON'T: source $HOME/.local/bin/env && python script.py
# ✅ DO: uv run python script.py (uses project .venv automatically)
```

#### For Virtual Environment Management
```bash
# uv automatically manages virtual environments
# No need for manual venv creation

# To see current environment
uv venv --show

# To sync dependencies (like pip install -r requirements.txt)
uv sync
```

#### Project Setup
```bash
# Initialize new project
uv init --python 3.11

# Add to existing project
uv init

# Install project in development mode
uv add --editable .
```

### Emergency Fallback

If uv is absolutely not available and you must use pip:

1. First try to install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
2. If that fails, document why pip was used in commit message
3. Convert to uv as soon as possible

### Benefits Observed

- **Fast installs**: Package installation is noticeably faster
- **Clean environments**: No more dependency conflicts
- **Reproducible builds**: Exactly the same dependencies for all developers
- **Better caching**: Shared package cache across projects
- **Modern workflow**: Integrates well with modern Python development

### Migration Commands

If you have an existing project with pip:

```bash
# Convert requirements.txt to uv
uv add $(cat requirements.txt | grep -v "^#" | grep -v "^$" | tr '\n' ' ')

# Or migrate from pyproject.toml
uv sync
```

---

**Remember**: Always use `uv add` - it's faster, safer, and more reliable than pip!