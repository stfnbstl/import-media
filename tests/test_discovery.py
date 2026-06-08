from file_handling.discovery import find_media_files
from utils.validation.file_types import FileType


def test_find_media_files_empty_dir(source_dir, mock_logger):
    """Test finding media files in an empty directory."""
    files = find_media_files(
        source_path=source_dir, filetype=FileType.IMAGE, log=mock_logger
    )
    assert len(files) == 0
    mock_logger.warning.assert_called_once()


def test_find_image_files(source_dir, mock_logger, sample_jpg_file):
    """Test finding image files in a directory with one JPG file."""
    files = find_media_files(
        source_path=source_dir, filetype=FileType.IMAGE, log=mock_logger
    )
    assert len(files) == 1
    assert files[0] == sample_jpg_file


def test_find_video_files(source_dir, mock_logger, sample_mp4_file):
    """Test finding video files in a directory with one MP4 file."""
    files = find_media_files(
        source_path=source_dir, filetype=FileType.VIDEO, log=mock_logger
    )
    assert len(files) == 1
    assert files[0] == sample_mp4_file


def test_find_image_files_mixed_content(source_dir, mock_logger, sample_jpg_file):
    """Test finding image files in a directory with mixed content."""
    # Create some non-image files
    (source_dir / "text_file.txt").write_text("This is a text file")
    (source_dir / "another_file.png").write_bytes(b"fake png data")

    files = find_media_files(
        source_path=source_dir, filetype=FileType.IMAGE, log=mock_logger
    )
    assert len(files) == 1
    assert files[0] == sample_jpg_file


def test_find_video_files_mixed_content(source_dir, mock_logger, sample_mp4_file):
    """Test finding video files in a directory with mixed content."""
    # Create some non-video files
    (source_dir / "text_file.txt").write_text("This is a text file")
    (source_dir / "another_file.jpg").write_bytes(b"fake jpg data")

    files = find_media_files(
        source_path=source_dir, filetype=FileType.VIDEO, log=mock_logger
    )
    assert len(files) == 1
    assert files[0] == sample_mp4_file


def test_find_media_files_ignores_hidden(source_dir, mock_logger):
    """Test that find_media_files ignores hidden image files."""
    hidden_jpg = source_dir / "._hidden.JPG"
    hidden_jpg.write_bytes(b"fake jpg data")

    files = find_media_files(
        source_path=source_dir, filetype=FileType.IMAGE, log=mock_logger
    )
    assert len(files) == 0
    mock_logger.warning.assert_called_once()


def test_find_image_files_case_insensitive(source_dir, mock_logger):
    """Test that find_media_files is case insensitive for image extensions."""
    upper_jpg = source_dir / "UPPER.JPG"
    upper_jpg.write_bytes(b"fake jpg data")

    lower_jpg = source_dir / "lower.jpg"
    lower_jpg.write_bytes(b"fake jpg data")

    upper_heif = source_dir / "UPPER.HEIF"
    upper_heif.write_bytes(b"fake heif data")

    lower_heic = source_dir / "lower.heic"
    lower_heic.write_bytes(b"fake heic data")

    files = find_media_files(
        source_path=source_dir, filetype=FileType.IMAGE, log=mock_logger
    )
    assert len(files) == 4
    file_names = [f.name for f in files]
    assert "UPPER.JPG" in file_names
    assert "lower.jpg" in file_names
    assert "UPPER.HEIF" in file_names
    assert "lower.heic" in file_names


def test_find_image_files_includes_heif_formats(source_dir, mock_logger):
    """Test finding supported HEIF-family image formats."""
    hif_file = source_dir / "image.hif"
    hif_file.write_bytes(b"fake hif data")

    heif_file = source_dir / "image.heif"
    heif_file.write_bytes(b"fake heif data")

    heic_file = source_dir / "image.heic"
    heic_file.write_bytes(b"fake heic data")

    files = find_media_files(
        source_path=source_dir, filetype=FileType.IMAGE, log=mock_logger
    )
    assert len(files) == 3
    file_names = [f.name for f in files]
    assert "image.hif" in file_names
    assert "image.heif" in file_names
    assert "image.heic" in file_names


def test_find_video_files_case_insensitive(source_dir, mock_logger):
    """Test that find_video_files is case insensitive for video extension."""
    upper_mp4 = source_dir / "UPPER.MP4"
    upper_mp4.write_bytes(b"fake mp4 data")

    lower_mp4 = source_dir / "lower.mp4"
    lower_mp4.write_bytes(b"fake mp4 data")

    files = find_media_files(
        source_path=source_dir, filetype=FileType.VIDEO, log=mock_logger
    )
    assert len(files) == 2
    file_names = [f.name for f in files]
    assert "UPPER.MP4" in file_names
    assert "lower.mp4" in file_names
