package backup

import (
	"fmt"
	"os"
	"path/filepath"
	"testing"
)

func TestFileExists(t *testing.T) {
	tmp := t.TempDir()
	path := filepath.Join(tmp, "test.txt")
	if FileExists(path) {
		t.Error("file should not exist yet")
	}
	os.WriteFile(path, []byte("hello"), 0644)
	if !FileExists(path) {
		t.Error("file should exist now")
	}
}

func TestCreate(t *testing.T) {
	tmp := t.TempDir()
	path := filepath.Join(tmp, "test.txt")
	content := []byte("original content")
	os.WriteFile(path, content, 0644)

	backupPath, err := Create(path)
	if err != nil {
		t.Fatalf("Create failed: %v", err)
	}

	backupData, err := os.ReadFile(backupPath)
	if err != nil {
		t.Fatalf("reading backup: %v", err)
	}
	if string(backupData) != string(content) {
		t.Errorf("backup content mismatch: got %q, want %q", backupData, content)
	}
}

func TestCreateNonExistent(t *testing.T) {
	_, err := Create("/nonexistent/path/file.txt")
	if err == nil {
		t.Error("expected error for non-existent file")
	}
}

func TestCreateOnDirectory(t *testing.T) {
	_, err := Create(t.TempDir())
	if err == nil {
		t.Error("expected error when backing up a directory")
	}
}

func TestCleanOld(t *testing.T) {
	tmp := t.TempDir()
	basePath := filepath.Join(tmp, "config.env")

	for i := range 5 {
		p := basePath + ".bak-" + fmt.Sprintf("2024010100000%d", i)
		os.WriteFile(p, []byte("backup"), 0644)
	}

	err := CleanOld(basePath, 2)
	if err != nil {
		t.Fatalf("CleanOld failed: %v", err)
	}

	matches, _ := filepath.Glob(basePath + ".bak-*")
	if len(matches) > 2 {
		t.Errorf("expected at most 2 backups, got %d", len(matches))
	}
}
