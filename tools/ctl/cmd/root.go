package cmd

import (
	"fmt"
	"os"

	"github.com/spf13/cobra"
)

var rootCmd = &cobra.Command{
	Use:   "ctl",
	Short: "SaaS infrastructure management tool",
	Long: `ctl manages the SaaS development stack:
  - Interactive setup wizard for first-time configuration
  - Certificate generation (CA + wildcard TLS)
  - Docker Compose lifecycle management`,
	RunE: func(cmd *cobra.Command, args []string) error {
		return cmd.Help()
	},
}

func Execute() {
	if err := rootCmd.Execute(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
