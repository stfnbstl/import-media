SOURCE_DESCRIPTION = "The source directory of the jpg files"
DESTINATION_DESCRIPTION = "The destination directory of the jpg files"
STRATEGY_DESCRIPTION = """The strategy to use when importing the files.\n
Options:\n
- [bold italic green]replace[/bold italic green]: Replace the file if it already exists.\n
- [bold italic green]onlynew[/bold italic green]: Only import files that do not already exist.\n
- [bold italic green]rename[/bold italic green]: Rename the new file if it already exists.\n
"""
LOG_FORMAT = "%(message)s"
BUFFER_SIZE = 65536  # 64KB
