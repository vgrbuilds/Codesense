# defining all ingestion constants in one place
ALLOWED_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".md", ".txt",
    ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".sh",
    ".java", ".c", ".cpp", ".h", ".cs", ".go", ".rb", ".php",
    ".rs",
}

IGNORE_DIRS = {"node_modules", ".git", "__pycache__", ".venv", "venv"}
MAX_LINES_PER_CHUNK = 200
CHUNK_OVERLAP = 20
BATCH_SIZE = 500

EXTENSION_LANGUAGE_MAP = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".jsx": "javascript",
    ".md": "markdown",
    ".java": "java",
    ".c": "c",
    ".cpp": "cpp",
    ".h": "c",
    ".cs": "csharp",
    ".go": "go",
    ".rb": "ruby",
    ".php": "php",
    ".rs": "rust",
    ".sh": "bash",
    ".json": "json",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml",
    ".ini": "ini",
    ".cfg": "ini",
    ".txt": "text",
}

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".bmp"}
DOCUMENT_EXTENSIONS = {".pdf", ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx", ".txt", ".md"}
