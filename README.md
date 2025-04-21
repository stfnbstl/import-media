# Media Import Tool

A command-line utility for importing and organizing media files (currently JPG images and MP4/LRF/MOV videos) from a source directory to a destination directory, using EXIF or file modification date to create a structured year/month/day folder hierarchy.

## Features

- **Automatic Date Organization**: Organizes media files into a Year/Month/Day folder structure based on EXIF data (for images) or file modification date (for videos or images without EXIF).
- **Supports Specific File Types**: Imports JPG images and MP4, LRF, MOV video formats.
- **Multiple Import Strategies**:
  - **replace**: Replace files if they already exist in the destination.
  - **onlynew**: Only import files that don't already exist in the destination.
  - **rename**: Rename the new file if it already exists in the destination.
- **Flexible Comparison Modes**: Choose how to compare existing files:
  - **full**: Compare files using the full SHA256 hash (default, safest but slower).
  - **partial**: Compare files using a partial hash (faster, good for large files, slightly less safe).
- **File Integrity**: Uses SHA256 hash verification (full or partial comparison mode) to help ensure file integrity.
- **Force Option**: Bypass comparison checks for faster imports when needed (use with caution).
- **Verbose Logging**: Detailed logging option for troubleshooting.

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd import-media
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
python main.py --source /path/to/source/folder --destination /path/to/destination/folder --filetype image
python main.py --source /path/to/source/folder --destination /path/to/destination/folder --filetype video
```

### Command Line Options

| Option | Description |
|--------|-------------|
| `--source` | Source directory containing media files |
| `--destination` | Destination directory where files will be organized |
| `--filetype` | Type of files to import: `image` (for JPG) or `video` (for MP4/LRF/MOV) |
| `--strategy` | Import strategy: `replace`, `onlynew` (default), or `rename` |
| `--comparison-mode` | How to compare existing files: `full` (default) or `partial` |
| `--verbose` | Enable detailed logging |
| `--force` | Skip comparison when replacing or checking for new files |

### Examples

Import JPG images, only copying new ones (using default full hash comparison):
```bash
python main.py --source /Volumes/SD_CARD/DCIM/100MEDIA --destination ~/Pictures --filetype image
```

Import videos, replacing existing files, comparing by partial hash:
```bash
python main.py --source /Volumes/SD_CARD/PRIVATE/AVCHD/BDMV/STREAM --destination ~/Videos --filetype video --strategy replace --comparison-mode partial
```

Force import of images without any comparison:
```bash
python main.py --source /Volumes/SD_CARD/DCIM/100MEDIA --destination ~/Pictures --filetype image --force
```

## Import Strategies Explained

- **replace**: If a file exists in the destination (determined by the chosen `--comparison-mode`), it will be overwritten by the source file. Hash comparison (`full` or `partial`) is used unless `--force` is specified.

- **onlynew** (default): Only imports files that don't already exist in the destination, based on the chosen `--comparison-mode`.

- **rename**: If a file exists in the destination (determined by the chosen `--comparison-mode`), the imported file will be renamed by appending a number (e.g., image_01.jpg).

## Comparison Modes Explained

- **full** (default): Calculates and compares the full SHA256 hash of the source file with potential destination files. This is the most reliable way to detect identical files but can be slower.
- **partial**: Compares a partial hash (beginning and end chunks) of the files. Faster than `full`, especially for large files, but carries a small theoretical risk of hash collision (treating different files as identical).

## Folder Structure

Files will be organized in the following structure:

```
destination/
├── 2023/
│   ├── January/
│   │   ├── 01/
│   │   │   ├── IMG001.JPG
│   │   │   └── IMG002.JPG
│   │   └── 02/
│   │       └── IMG003.JPG
│   └── February/
│       └── ...
└── 2024/
    └── ...
```

## Requirements
- Python 3.6 or higher
- rich==13.7.1
- pillow==10.3.0
- typer==0.12.3
- python-dotenv  # (If applicable, ensure requirements.txt is updated)

## Testing

The application includes a comprehensive test suite using pytest. To run the tests:

```bash
# Install test dependencies
pip install -r requirements.txt

# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run a specific test module
pytest tests/test_strategies.py

# Run tests with coverage report
pytest --cov=. tests/
```

### Testing Strategy
- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test how components work together
- **Mocking**: External dependencies and file system operations are mocked for reliable tests
- **Fixtures**: Common test data and setup is handled through pytest fixtures

To add coverage reporting, install pytest-cov:
```bash
pip install pytest-cov
```