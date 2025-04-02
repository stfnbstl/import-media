# JPG Import Tool

A command-line utility for importing and organizing JPG files from a source directory to a destination directory, using EXIF data to create a structured year/month/day folder hierarchy.

## Features

- **Automatic Date Organization**: Organizes photos into a Year/Month/Day folder structure based on EXIF data
- **Multiple Import Strategies**:
  - **replace**: Replace files if they already exist in the destination
  - **onlynew**: Only import files that don't already exist in the destination
  - **rename**: Rename the new file if it already exists in the destination
- **File Integrity**: Uses SHA256 hash verification to ensure file integrity
- **Force Option**: Bypass hash comparison for faster imports when needed
- **Verbose Logging**: Detailed logging option for troubleshooting

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
python main.py --source /path/to/source/folder --destination /path/to/destination/folder
```

### Command Line Options

| Option | Description |
|--------|-------------|
| `--source` | Source directory containing JPG files |
| `--destination` | Destination directory where files will be organized |
| `--strategy` | Import strategy: replace, onlynew (default), or rename |
| `--verbose` | Enable detailed logging |
| `--force` | Skip hash comparison when replacing or checking for new files |

### Examples

Import files, only copying new ones:
```bash
python main.py --source /Volumes/SD_CARD/DCIM/100FUJI --destination ~/Pictures
```

Replace existing files:
```bash
python main.py --source /Volumes/SD_CARD/DCIM/100FUJI --destination ~/Pictures --strategy replace
```

Rename files if they already exist:
```bash
python main.py --source /Volumes/SD_CARD/DCIM/100FUJI --destination ~/Pictures --strategy rename
```

Force import without hash comparison:
```bash
python main.py --source /Volumes/SD_CARD/DCIM/100FUJI --destination ~/Pictures --force
```

## Import Strategies Explained

- **replace**: If a file with the same name exists in the destination, it will be overwritten. The tool performs hash comparison (unless --force is used) to avoid unnecessary copying of identical files.

- **onlynew** (default): Only imports files that don't already exist in the destination. Uses hash comparison to identify truly unique files.

- **rename**: If a file with the same name exists in the destination, the imported file will be renamed by appending a number (e.g., image_01.jpg).

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