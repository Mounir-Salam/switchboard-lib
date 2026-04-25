import pytest
from switchboard.connectors.blob_storage.localfs import LocalFSConnector

def test_local_fs_write_and_read(tmp_path):
    # tmp_path is a built-in pytest fixture that provides a temporary directory
    base_dir = tmp_path / "data"
    storage = LocalFSConnector(base_dir)
    
    test_file = "hello.txt"
    test_content = "Switchboard Test"
    
    # Test writing
    storage.write(test_file, test_content)
    
    # Verify the file actually exists on disk in the temp folder
    assert (base_dir / test_file).exists()
    
    # Test reading
    content = storage.read(test_file).decode("utf-8")
    assert content == test_content
    print("##################### Storage")