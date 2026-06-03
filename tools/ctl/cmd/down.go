package cmd

import (
	"cotai-eus/saas/tools/ctl/internal/infra"

	"github.com/spf13/cobra"
)

var downCmd = &cobra.Command{
	Use:   "down",
	Short: "Stop all services",
	Long:  "Stop and remove containers, networks, and default volumes.",
	RunE: func(cmd *cobra.Command, args []string) error {
		return infra.DockerComposeCmd("down")
	},
}

func init() {
	rootCmd.AddCommand(downCmd)
}
