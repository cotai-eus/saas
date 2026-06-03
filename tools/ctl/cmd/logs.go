package cmd

import (
	"cotai-eus/saas/tools/ctl/internal/infra"

	"github.com/spf13/cobra"
)

var logFollow bool

var logsCmd = &cobra.Command{
	Use:   "logs [service...]",
	Short: "View logs from services",
	Long:  "Tail logs from one or more services. Leave empty for all services.",
	RunE: func(cmd *cobra.Command, args []string) error {
		composeArgs := []string{"logs"}
		if logFollow {
			composeArgs = append(composeArgs, "-f")
		}
		composeArgs = append(composeArgs, args...)
		return infra.DockerComposeCmd(composeArgs...)
	},
}

func init() {
	logsCmd.Flags().BoolVarP(&logFollow, "follow", "f", true, "Follow log output")
	rootCmd.AddCommand(logsCmd)
}
