package cmd

import (
	"cotai-eus/saas/tools/ctl/internal/infra"

	"github.com/spf13/cobra"
)

var upCmd = &cobra.Command{
	Use:   "up",
	Short: "Start all services with Docker Compose",
	Long:  "Start the full SaaS stack: traefik, keycloak, databases, and apps.",
	RunE: func(cmd *cobra.Command, args []string) error {
		return infra.DockerComposeCmd("up", "-d")
	},
}

func init() {
	rootCmd.AddCommand(upCmd)
}
