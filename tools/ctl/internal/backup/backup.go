package backup

import (
	"fmt"
	"io"
	"os"
	"path/filepath"
	"sort"
	"time"
)

func FileExists(path string) bool {
	_, err := os.Stat(path)
	return err == nil
}

func Create(path string) (string, error) {
	info, err := os.Stat(path)
	if err != nil {
		return "", fmt.Errorf("stat %s: %w", path, err)
	}
	if info.IsDir() {
		return "", fmt.Errorf("%s is a directory", path)
	}

	timestamp := time.Now().Format("20060102150405")
	backupPath := path + ".bak-" + timestamp

	src, err := os.Open(path)
	if err != nil {
		return "", err
	}
	defer src.Close()

	dst, err := os.OpenFile(backupPath, os.O_CREATE|os.O_WRONLY|os.O_TRUNC, info.Mode())
	if err != nil {
		return "", err
	}
	defer dst.Close()

	_, err = io.Copy(dst, src)
	if err != nil {
		return "", err
	}

	return backupPath, nil
}

func CleanOld(basePath string, keep int) error {
	dir := filepath.Dir(basePath)
	base := filepath.Base(basePath)
	pattern := base + ".bak-*"

	matches, err := filepath.Glob(filepath.Join(dir, pattern))
	if err != nil {
		return err
	}

	sort.Slice(matches, func(i, j int) bool {
		return matches[i] > matches[j]
	})

	if len(matches) > keep {
		for _, m := range matches[keep:] {
			os.Remove(m)
		}
	}

	return nil
}
