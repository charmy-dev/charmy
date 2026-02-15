# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.resolve()
sys.path.insert(0, str(project_root))

# 验证路径是否正确
print(f"Project root: {project_root}")
print(f"Charmy package path: {project_root / 'charmy'}")

project = "Charmy GUI"
copyright = "2026, XiangQinxi, rgzz666, littlewhitecloud"
author = "XiangQinxi, rgzz666, littlewhitecloud"
release = "0.1.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "myst_parser", "sphinx_design",
    'sphinx.ext.autodoc',
    # 'sphinx.ext.napoleon',  # 暂时禁用，避免递归深度错误
    'sphinx.ext.doctest',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.mathjax',
]
myst_enable_extensions = ["colon_fence"]

templates_path = ["_templates"]
exclude_patterns = []


# -- Options for autodoc extension ------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html

# 防止递归深度错误的关键配置
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__',
    'show-inheritance': True,
}

# 禁用继承的文档字符串处理
autodoc_inherit_docstrings = False

# 设置Python路径
sys.path.insert(0, str(project_root))

# 跳过某些可能导致递归的模块
def skip_recursive_members(app, what, name, obj, skip, options):
    # 跳过可能导致递归的模块
    if name in ['charmy', 'charmy.widgets', 'charmy.styles', 'charmy.drawing']:
        return True
    return skip

def setup(app):
    app.connect('autodoc-skip-member', skip_recursive_members)

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = ["_static"]
html_theme_options = {
    "light_css_variables": {
        "color-brand-primary": "red",
        "color-brand-content": "#CC3333",
        "color-admonition-background": "orange",
    },
}