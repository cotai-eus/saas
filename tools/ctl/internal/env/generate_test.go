package env

import (
	"os"
	"strings"
	"testing"
)

func TestGenerateDev(t *testing.T) {
	cfg := Config{BaseDomain: "local.dev", EnvType: "dev"}
	result, err := Generate(cfg)
	if err != nil {
		t.Fatalf("Generate failed: %v", err)
	}
	content := string(result.Content)

	if !strings.Contains(content, "BASE_DOMAIN=local.dev") {
		t.Errorf("expected BASE_DOMAIN=local.dev, got:\n%s", content)
	}
	if !strings.Contains(content, "AUTH_HOST=auth.local.dev") {
		t.Errorf("expected AUTH_HOST=auth.local.dev")
	}
	if strings.Contains(content, "TLS_RESOLVER=letsencrypt") {
		t.Errorf("dev env should not set letsencrypt resolver")
	}
}

func TestGenerateProd(t *testing.T) {
	cfg := Config{BaseDomain: "example.com", EnvType: "prod"}
	result, err := Generate(cfg)
	if err != nil {
		t.Fatalf("Generate failed: %v", err)
	}
	content := string(result.Content)

	if !strings.Contains(content, "TLS_RESOLVER=letsencrypt") {
		t.Errorf("prod env should set letsencrypt resolver")
	}
	if !strings.Contains(content, "OAUTH2_PROXY_SSL_INSECURE=false") {
		t.Errorf("prod env should set SSL insecure false")
	}
}

func TestGenerateSecrets(t *testing.T) {
	cfg := Config{BaseDomain: "local.dev", EnvType: "dev"}
	result, err := Generate(cfg)
	if err != nil {
		t.Fatalf("Generate failed: %v", err)
	}

	required := []string{"KC_DB_PASSWORD", "DB_PASSWORD", "KC_ADMIN_PASSWORD",
		"OAUTH2_PROXY_CLIENT_SECRET", "SAAS_API_CLIENT_SECRET",
		"OAUTH2_PROXY_COOKIE_SECRET"}
	for _, key := range required {
		if _, ok := result.Secrets[key]; !ok {
			t.Errorf("expected secret %s to be generated", key)
		}
	}
}

func TestGenerateEmptyDomain(t *testing.T) {
	cfg := Config{BaseDomain: "", EnvType: "dev"}
	result, err := Generate(cfg)
	if err != nil {
		t.Fatalf("Generate failed: %v", err)
	}
	content := string(result.Content)

	if strings.Contains(content, "AUTH_HOST=auth.") && !strings.Contains(content, "AUTH_HOST=auth.local.dev") {
		t.Logf("empty domain yields: %s", content)
	}
}

func TestEnvExampleEmbedded(t *testing.T) {
	if len(templateData) == 0 {
		t.Fatal("templateData is empty, .env.example not embedded")
	}
	if !strings.Contains(string(templateData), "BASE_DOMAIN") {
		t.Error("template must contain BASE_DOMAIN placeholder")
	}
}

func TestGenerateStaging(t *testing.T) {
	cfg := Config{BaseDomain: "staging.example.com", EnvType: "staging"}
	result, err := Generate(cfg)
	if err != nil {
		t.Fatalf("Generate failed: %v", err)
	}
	content := string(result.Content)

	if !strings.Contains(content, "API_HOST=api.staging.example.com") {
		t.Errorf("expected staging API host")
	}
	if !strings.Contains(content, "TRAEFIK_HOST=traefik.staging.example.com") {
		t.Errorf("expected staging traefik host")
	}
}

func TestGenerateNoTLSInDev(t *testing.T) {
	cfg := Config{BaseDomain: "local.dev", EnvType: "dev"}
	result, err := Generate(cfg)
	if err != nil {
		t.Fatalf("Generate failed: %v", err)
	}
	content := string(result.Content)

	if strings.Contains(content, "TLS_RESOLVER=letsencrypt") {
		t.Errorf("dev should not have letsencrypt TLS resolver")
	}
}

func testLoadEnvFile(t *testing.T) {
	data, err := os.ReadFile("../../infra/.env.example")
	if err != nil {
		t.Fatalf("cannot read .env.example: %v", err)
	}
	lines := strings.Split(string(data), "\n")
	var keys []string
	for _, line := range lines {
		line = strings.TrimSpace(line)
		if line == "" || strings.HasPrefix(line, "#") {
			continue
		}
		parts := strings.SplitN(line, "=", 2)
		if len(parts) == 2 {
			keys = append(keys, parts[0])
		}
	}

	requiredKeys := []string{
		"BASE_DOMAIN", "AUTH_HOST", "APP_HOST", "API_HOST",
		"KC_DB_PASSWORD", "DB_PASSWORD", "OAUTH2_PROXY_CLIENT_SECRET",
	}
	for _, k := range requiredKeys {
		found := false
		for _, key := range keys {
			if key == k {
				found = true
				break
			}
		}
		if !found {
			t.Errorf("required key %s not found in .env.example", k)
		}
	}
}
