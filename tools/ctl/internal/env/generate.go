package env

import (
	_ "embed"
	"fmt"
	"strings"

	"cotai-eus/saas/tools/ctl/internal/secrets"
)

//go:embed .env.example
var templateData []byte

type Config struct {
	BaseDomain string
	EnvType    string
}

type Result struct {
	Content []byte
	Secrets map[string]string
}

func Generate(cfg Config) (*Result, error) {
	lines := strings.Split(string(templateData), "\n")
	var result []string
	secretsMap := make(map[string]string)

	for _, line := range lines {
		trimmed := strings.TrimSpace(line)

		if trimmed == "" || strings.HasPrefix(trimmed, "#") {
			result = append(result, line)
			continue
		}

		eqIdx := strings.Index(line, "=")
		if eqIdx < 0 {
			result = append(result, line)
			continue
		}

		key := strings.TrimSpace(line[:eqIdx])
		rawValue := line[eqIdx+1:]
		value := strings.TrimSpace(rawValue)

		switch key {
		case "BASE_DOMAIN":
			value = cfg.BaseDomain
		case "AUTH_HOST":
			value = "auth." + cfg.BaseDomain
		case "APP_HOST":
			value = "app." + cfg.BaseDomain
		case "API_HOST":
			value = "api." + cfg.BaseDomain
		case "TRAEFIK_HOST":
			value = "traefik." + cfg.BaseDomain
		case "LETSENCRYPT_EMAIL":
			if value == "" {
				value = "admin@" + cfg.BaseDomain
			}
		case "KC_DB_PASSWORD", "DB_PASSWORD", "KC_ADMIN_PASSWORD",
			"OAUTH2_PROXY_CLIENT_SECRET", "SAAS_API_CLIENT_SECRET",
			"OAUTH2_PROXY_COOKIE_SECRET":
			if value == "" {
				pwd, err := secrets.GenerateHex(16)
				if err != nil {
					return nil, fmt.Errorf("generating secret for %s: %w", key, err)
				}
				value = pwd
				secretsMap[key] = pwd
			}
		case "OAUTH2_PROXY_SSL_INSECURE":
			if cfg.EnvType == "prod" {
				value = "false"
			} else {
				value = "true"
			}
		}

		result = append(result, key+"="+value)
	}

	return &Result{
		Content: []byte(strings.Join(result, "\n")),
		Secrets: secretsMap,
	}, nil
}
