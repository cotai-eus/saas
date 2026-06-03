package cmd

import (
	"fmt"

	"cotai-eus/saas/tools/ctl/internal/setup"
	"cotai-eus/saas/tools/ctl/internal/tui"

	"github.com/spf13/cobra"
)

var (
	setupDomain       string
	setupEnvType      string
	setupNoInteractive bool
	setupNoBackup     bool
	setupSkipTLS      bool
)

var setupCmd = &cobra.Command{
	Use:   "setup",
	Short: "Configure the SaaS infrastructure",
	Long: `Interactive or non-interactive setup of the entire stack.

Interactive mode (default): guides you through domain, environment, backup,
certificate generation, and Docker network setup.

Non-interactive mode (--no-interactive): for CI/CD pipelines and automation.`,
	RunE: func(cmd *cobra.Command, args []string) error {
		if setupNoInteractive {
			return nonInteractiveSetup()
		}
		return tui.RunSetup()
	},
}

func nonInteractiveSetup() error {
	fmt.Println("ctl setup -- no-interactive mode")
	fmt.Println()

	fmt.Printf("Domain: %s\n", setupDomain)
	fmt.Printf("Environment: %s\n", setupEnvType)
	fmt.Println()

	cfg := setup.Config{
		Domain:  setupDomain,
		EnvType: setupEnvType,
		Backup:  !setupNoBackup,
		SkipTLS: setupSkipTLS,
	}

	result, err := setup.Run(cfg)
	if err != nil {
		return fmt.Errorf("setup failed: %w", err)
	}

	for _, b := range result.Backups {
		fmt.Printf("  ✓ Backed up: %s\n", b)
	}
	if result.CertGenerated {
		fmt.Println("  ✓ Generated TLS certificates")
	}
	fmt.Printf("  ✓ Created %s\n", result.EnvPath)
	fmt.Println("  ✓ Ensured Docker network 'proxy'")

	if len(result.Secrets) > 0 {
		fmt.Println()
		fmt.Println("Generated secrets:")
		for k := range result.Secrets {
			fmt.Printf("  %s=***\n", k)
		}
	}

	fmt.Println()
	fmt.Println("Setup complete! Run './ctl up' to start the stack.")
	return nil
}

func init() {
	setupCmd.Flags().StringVar(&setupDomain, "domain", "local.dev", "Base domain (e.g. local.dev)")
	setupCmd.Flags().StringVar(&setupEnvType, "env", "dev", "Environment type: dev, staging, prod")
	setupCmd.Flags().BoolVar(&setupNoInteractive, "no-interactive", false, "Run in non-interactive mode for CI/CD")
	setupCmd.Flags().BoolVar(&setupNoBackup, "no-backup", false, "Skip backup of existing files")
	setupCmd.Flags().BoolVar(&setupSkipTLS, "skip-tls", false, "Skip TLS certificate generation")

	rootCmd.AddCommand(setupCmd)
}
