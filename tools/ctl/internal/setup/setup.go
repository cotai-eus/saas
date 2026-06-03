package setup

import (
	"fmt"
	"os"

	"cotai-eus/saas/tools/ctl/internal/backup"
	"cotai-eus/saas/tools/ctl/internal/cert"
	"cotai-eus/saas/tools/ctl/internal/env"
	"cotai-eus/saas/tools/ctl/internal/infra"
)

type Config struct {
	Domain  string
	EnvType string
	Backup  bool
	SkipTLS bool
}

type Result struct {
	Backups       []string
	EnvPath       string
	Secrets       map[string]string
	CertGenerated bool
	NetworkReady  bool
}

func Run(cfg Config) (*Result, error) {
	result := &Result{}

	if cfg.Backup {
		files := []string{infra.EnvFile, infra.WildcardCert, infra.WildcardKey}
		for _, f := range files {
			if backup.FileExists(f) {
				path, err := backup.Create(f)
				if err != nil {
					return nil, fmt.Errorf("backup %s: %w", f, err)
				}
				result.Backups = append(result.Backups, path)
			}
		}
		backup.CleanOld(infra.EnvFile, 5)
	}

	if !cfg.SkipTLS {
		ca, err := cert.GenerateCA()
		if err != nil {
			return nil, fmt.Errorf("CA generation: %w", err)
		}

		caPair, err := ca.PEM()
		if err != nil {
			return nil, fmt.Errorf("CA PEM: %w", err)
		}
		if err := cert.WritePEM(infra.RootCACert, caPair.CertPEM); err != nil {
			return nil, fmt.Errorf("writing CA cert: %w", err)
		}
		if err := cert.WritePEM(infra.RootCAKey, caPair.KeyPEM); err != nil {
			return nil, fmt.Errorf("writing CA key: %w", err)
		}

		wildcard, err := ca.GenerateWildcard(cfg.Domain)
		if err != nil {
			return nil, fmt.Errorf("wildcard cert: %w", err)
		}
		if err := cert.WritePEM(infra.WildcardCert, wildcard.CertPEM); err != nil {
			return nil, fmt.Errorf("writing wildcard cert: %w", err)
		}
		if err := cert.WritePEM(infra.WildcardKey, wildcard.KeyPEM); err != nil {
			return nil, fmt.Errorf("writing wildcard key: %w", err)
		}

		result.CertGenerated = true
	}

	envResult, err := env.Generate(env.Config{
		BaseDomain: cfg.Domain,
		EnvType:    cfg.EnvType,
	})
	if err != nil {
		return nil, fmt.Errorf("env generation: %w", err)
	}
	if err := os.WriteFile(infra.EnvFile, envResult.Content, 0644); err != nil {
		return nil, fmt.Errorf("writing .env: %w", err)
	}
	result.EnvPath = infra.EnvFile
	result.Secrets = envResult.Secrets

	if err := infra.EnsureNetwork(infra.NetworkName); err != nil {
		return nil, fmt.Errorf("docker network: %w", err)
	}
	result.NetworkReady = true

	return result, nil
}
