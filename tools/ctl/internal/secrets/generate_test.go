package secrets

import (
	"strings"
	"testing"
)

func TestGenerateHexLength(t *testing.T) {
	secret, err := GenerateHex(16)
	if err != nil {
		t.Fatalf("GenerateHex failed: %v", err)
	}
	if len(secret) != 32 {
		t.Errorf("expected 32 hex chars for 16 bytes, got %d: %s", len(secret), secret)
	}
}

func TestGenerateHexEmpty(t *testing.T) {
	secret, err := GenerateHex(0)
	if err != nil {
		t.Fatalf("GenerateHex(0) failed: %v", err)
	}
	if secret != "" {
		t.Errorf("expected empty string for 0 bytes, got %q", secret)
	}
}

func TestGenerateHexRandomness(t *testing.T) {
	s1, _ := GenerateHex(16)
	s2, _ := GenerateHex(16)
	if s1 == s2 {
		t.Error("two sequential calls produced the same result")
	}
}

func TestGenerateHexValidHex(t *testing.T) {
	secret, err := GenerateHex(8)
	if err != nil {
		t.Fatalf("GenerateHex failed: %v", err)
	}
	for _, c := range secret {
		if !strings.ContainsRune("0123456789abcdef", c) {
			t.Errorf("invalid hex character %c in %s", c, secret)
		}
	}
}

func TestGenerateHexMultipleLengths(t *testing.T) {
	for _, length := range []int{1, 4, 8, 16, 32, 64} {
		secret, err := GenerateHex(length)
		if err != nil {
			t.Fatalf("GenerateHex(%d) failed: %v", length, err)
		}
		expectedLen := length * 2
		if len(secret) != expectedLen {
			t.Errorf("expected %d chars for %d bytes, got %d", expectedLen, length, len(secret))
		}
	}
}

func TestGenerateHexNotNil(t *testing.T) {
	secret, err := GenerateHex(1)
	if err != nil {
		t.Fatalf("GenerateHex failed: %v", err)
	}
	if secret == "" {
		t.Error("expected non-empty string for 1 byte")
	}
}