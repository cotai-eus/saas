package infra

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
)

const (
	NetworkName = "proxy"
)

var (
	RepoRoot     string
	ComposeFile  string
	CertsDir     string
	EnvFile      string
	EnvExample   string
	WildcardCert string
	WildcardKey  string
	RootCACert   string
	RootCAKey    string
)

func init() {
	root, err := findRepoRoot()
	if err != nil {
		root = "."
	}
	RepoRoot = root
	ComposeFile = filepath.Join(root, "infra", "docker-compose.yml")
	CertsDir = filepath.Join(root, "infra", "traefik", "certs")
	EnvFile = filepath.Join(root, "infra", ".env")
	EnvExample = filepath.Join(root, "infra", ".env.example")
	WildcardCert = filepath.Join(root, "infra", "traefik", "certs", "wildcard.crt")
	WildcardKey = filepath.Join(root, "infra", "traefik", "certs", "wildcard.key")
	RootCACert = filepath.Join(root, "infra", "traefik", "certs", "rootCA.pem")
	RootCAKey = filepath.Join(root, "infra", "traefik", "certs", "rootCA-key.pem")
}

func findRepoRoot() (string, error) {
	dir, err := os.Getwd()
	if err != nil {
		return "", err
	}
	dir, err = filepath.Abs(dir)
	if err != nil {
		return "", err
	}
	for {
		composePath := filepath.Join(dir, "infra", "docker-compose.yml")
		if _, err := os.Stat(composePath); err == nil {
			return dir, nil
		}
		parent := filepath.Dir(dir)
		if parent == dir {
			return "", fmt.Errorf("cannot find repo root (infra/docker-compose.yml not found in any parent)")
		}
		dir = parent
	}
}

func EnsureNetwork(name string) error {
	cmd := exec.Command("docker", "network", "ls", "--filter", "name="+name, "--format", "{{.Name}}")
	out, err := cmd.Output()
	if err != nil {
		return fmt.Errorf("checking network: %w", err)
	}

	if strings.TrimSpace(string(out)) == name {
		return nil
	}

	cmd = exec.Command("docker", "network", "create", name)
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	if err := cmd.Run(); err != nil {
		return fmt.Errorf("creating network %s: %w", name, err)
	}

	return nil
}

func DockerComposeCmd(args ...string) error {
	cmd := exec.Command("docker", append([]string{"compose", "-f", ComposeFile}, args...)...)
	cmd.Stdin = os.Stdin
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	return cmd.Run()
}
