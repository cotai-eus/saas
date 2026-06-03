package cmd

import (
	"fmt"
	"os"

	"cotai-eus/saas/tools/ctl/internal/infra"

	"github.com/spf13/cobra"
)

var (
	cleanVolumes bool
	cleanCerts   bool
	cleanForce   bool
)

var cleanCmd = &cobra.Command{
	Use:   "clean",
	Short: "Remove containers, volumes, and certificates",
	Long: `Stop all services and optionally remove volumes, certificates, and .env.

Flags control what gets removed:
  --volumes: remove database volumes (data loss!)
  --certs:   remove generated TLS certificates
  --force:   skip confirmation prompts`,
	RunE: func(cmd *cobra.Command, args []string) error {
		if !cleanForce {
			fmt.Print("This will stop all services.")
			if cleanVolumes {
				fmt.Print(" Database volumes will be DELETED (data loss).")
			}
			fmt.Print(" Continue? [y/N]: ")
			var response string
			fmt.Scanln(&response)
			if response != "y" && response != "Y" {
				fmt.Println("Aborted.")
				return nil
			}
		}

		composeArgs := []string{"down"}
		if cleanVolumes {
			composeArgs = append(composeArgs, "-v")
		}
		if err := infra.DockerComposeCmd(composeArgs...); err != nil {
			return err
		}

		if cleanCerts {
			for _, f := range []string{infra.WildcardCert, infra.WildcardKey, infra.RootCACert, infra.RootCAKey} {
				if err := os.Remove(f); err != nil && !os.IsNotExist(err) {
					return fmt.Errorf("removing %s: %w", f, err)
				}
				fmt.Printf("  Removed %s\n", f)
			}
		}

		fmt.Println("Clean complete.")
		return nil
	},
}

func init() {
	cleanCmd.Flags().BoolVar(&cleanVolumes, "volumes", false, "Remove Docker volumes (data loss)")
	cleanCmd.Flags().BoolVar(&cleanCerts, "certs", false, "Remove generated TLS certificates")
	cleanCmd.Flags().BoolVarP(&cleanForce, "force", "f", false, "Skip confirmation prompts")
	rootCmd.AddCommand(cleanCmd)
}
