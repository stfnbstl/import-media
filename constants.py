SOURCE_DESCRIPTION = "The source directory of the jpg files"
DESTINATION_DESCRIPTION = "The destination directory of the jpg files"
STRATEGY_DESCRIPTION = """The strategy to use when importing the files.\n
Options:\n
- [bold italic green]replace[/bold italic green]: Replace the file if it already exists.\n
- [bold italic green]onlynew[/bold italic green]: Only import files that do not already exist.\n
- [bold italic green]rename[/bold italic green]: Rename the new file if it already exists.\n
"""
FILETYPE_DESCRIPTION = """The type of file to import.\n
Options:\n
- [bold italic green]image[/bold italic green]: Import image files. (*.jpg)\n
- [bold italic green]video[/bold italic green]: Import video files. (*.mp4, *.lrf, *.mov)\n
"""
COMPARISON_MODE_DESCRIPTION = """The mode to use when comparing files.\n
Options:\n
- [bold italic green]full[/bold italic green]: Calculate the full hash of a file and compare it. (safe but slow)\n
- [bold italic green]partial[/bold italic green]: Compare a partial hash, i.e. beginning and end chunks of the hash. If those match, the files are considered identical. (not 100% safe but fast, recommended for large files)\n
"""
VERBOSE_DESCRIPTION = "Enable verbose mode"
LOG_FORMAT = "%(message)s"
BUFFER_SIZE = 65536  # 64KB
FORCE_DESCRIPTION = "Skip hash comparison when replacing or checking for new files"
