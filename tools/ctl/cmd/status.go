package cmd

import (
	"cotai-eus/saas/tools/ctl/internal/infra"

	"github.com/spf13/cobra"
)

var statusCmd = &cobra.Command{
	Use:   "status",
	Short: "Show container status",
	Long:  "Display the status of all services managed by Docker Compose.",
	RunE: func(cmd *cobra.Command, args []string) error {
		return infra.DockerComposeCmd("ps")
	},
}

func init() {
	rootCmd.AddCommand(statusCmd)
}
