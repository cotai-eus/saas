package tui

import (
	"fmt"
	"os"
	"strings"

	"cotai-eus/saas/tools/ctl/internal/backup"
	"cotai-eus/saas/tools/ctl/internal/cert"
	"cotai-eus/saas/tools/ctl/internal/env"
	"cotai-eus/saas/tools/ctl/internal/infra"

	"github.com/charmbracelet/bubbles/spinner"
	"github.com/charmbracelet/bubbles/textinput"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
)

type step int

const (
	stepWelcome step = iota
	stepDomain
	stepEnvironment
	stepBackup
	stepExecuting
	stepSummary
)

const (
	execStepBackup = iota
	execStepCert
	execStepEnv
	execStepNetwork
	execStepDone
)

type session struct {
	domain   string
	envType  string
	doBackup bool
	skipTLS  bool
}

type execProgressMsg struct {
	step    int
	message string
	err     error
}

type model struct {
	step    step
	session session
	err     error

	domainInput textinput.Model
	spin        spinner.Model

	envTypes  []string
	envCursor int

	progress []string

	width int
}

var (
	headerStyle = lipgloss.NewStyle().
			Bold(true).
			Foreground(lipgloss.Color("#7C3AED"))

	successStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color("#10B981"))

	errorStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color("#EF4444"))

	infoStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color("#6B7280"))

	highlightStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color("#F59E0B"))

	subtleStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color("#9CA3AF"))
)

func RunSetup() error {
	m := initialModel()
	p := tea.NewProgram(m)
	_, err := p.Run()
	return err
}

func initialModel() model {
	s := spinner.New()
	s.Style = lipgloss.NewStyle().Foreground(lipgloss.Color("#7C3AED"))
	s.Spinner = spinner.Dot

	ti := textinput.New()
	ti.Placeholder = "local.dev"
	ti.CharLimit = 100
	ti.Width = 40

	return model{
		step:        stepWelcome,
		domainInput: ti,
		spin:        s,
		envTypes:    []string{"dev", "staging", "prod"},
		envCursor:   0,
		session: session{
			domain:   "local.dev",
			envType:  "dev",
			doBackup: true,
		},
	}
}

func (m model) Init() tea.Cmd {
	return nil
}

func (m model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.WindowSizeMsg:
		m.width = msg.Width
		return m, nil

	case tea.KeyMsg:
		if msg.Type == tea.KeyCtrlC {
			return m, tea.Quit
		}

		switch m.step {
		case stepWelcome:
			if msg.Type == tea.KeyEnter {
				m.step = stepDomain
				m.domainInput.Focus()
				return m, textinput.Blink
			}
			return m, nil

		case stepDomain:
			if msg.Type == tea.KeyEnter {
				m.session.domain = strings.TrimSpace(m.domainInput.Value())
				if m.session.domain == "" {
					m.session.domain = "local.dev"
				}
				m.step = stepEnvironment
				m.domainInput.Blur()
				return m, nil
			}
			var cmd tea.Cmd
			m.domainInput, cmd = m.domainInput.Update(msg)
			return m, cmd

		case stepEnvironment:
			switch msg.Type {
			case tea.KeyUp, tea.KeyShiftTab:
				if m.envCursor > 0 {
					m.envCursor--
				}
			case tea.KeyDown, tea.KeyTab:
				if m.envCursor < len(m.envTypes)-1 {
					m.envCursor++
				}
			case tea.KeyEnter:
				m.session.envType = m.envTypes[m.envCursor]
				m.step = stepBackup
			}
			return m, nil

		case stepBackup:
			switch msg.Type {
			case tea.KeyLeft, tea.KeyRight:
				m.session.doBackup = !m.session.doBackup
			case tea.KeyEnter:
				m.step = stepExecuting
				return m, tea.Batch(m.spin.Tick, m.execStepCmd(execStepBackup))
			}
			return m, nil

		case stepExecuting:
			var cmd tea.Cmd
			m.spin, cmd = m.spin.Update(msg)
			return m, cmd

		case stepSummary:
			if msg.Type == tea.KeyEnter {
				return m, tea.Quit
			}
			return m, nil
		}

	case execProgressMsg:
		if msg.err != nil {
			m.err = msg.err
			m.step = stepSummary
			return m, nil
		}
		m.progress = append(m.progress, msg.message)
		nextStep := msg.step + 1
		if nextStep >= execStepDone {
			m.step = stepSummary
			return m, nil
		}
		return m, m.execStepCmd(nextStep)

	case spinner.TickMsg:
		if m.step == stepExecuting {
			var cmd tea.Cmd
			m.spin, cmd = m.spin.Update(msg)
			return m, cmd
		}
		return m, nil
	}

	return m, nil
}

func (m model) execStepCmd(step int) tea.Cmd {
	return func() tea.Msg {
		switch step {
		case execStepBackup:
			return m.doBackupStep()
		case execStepCert:
			return m.doCertStep()
		case execStepEnv:
			return m.doEnvStep()
		case execStepNetwork:
			return m.doNetworkStep()
		default:
			return execProgressMsg{step: execStepDone}
		}
	}
}

func (m model) doBackupStep() tea.Msg {
	if !m.session.doBackup {
		return execProgressMsg{step: execStepBackup, message: "Skipped backups"}
	}

	files := []string{infra.EnvFile, infra.WildcardCert, infra.WildcardKey}
	var backedUp int
	for _, f := range files {
		if backup.FileExists(f) {
			_, err := backup.Create(f)
			if err != nil {
				return execProgressMsg{step: execStepBackup, err: fmt.Errorf("backup %s: %w", f, err)}
			}
			backedUp++
		}
	}
	backup.CleanOld(infra.EnvFile, 5)

	if backedUp == 0 {
		return execProgressMsg{step: execStepBackup, message: "No existing files to backup"}
	}
	return execProgressMsg{step: execStepBackup, message: fmt.Sprintf("Backed up %d file(s)", backedUp)}
}

func (m model) doCertStep() tea.Msg {
	if m.session.skipTLS {
		return execProgressMsg{step: execStepCert, message: "Skipped TLS certificates"}
	}

	ca, err := cert.GenerateCA()
	if err != nil {
		return execProgressMsg{step: execStepCert, err: fmt.Errorf("CA generation: %w", err)}
	}

	caPair, err := ca.PEM()
	if err != nil {
		return execProgressMsg{step: execStepCert, err: fmt.Errorf("CA PEM: %w", err)}
	}
	if err := cert.WritePEM(infra.RootCACert, caPair.CertPEM); err != nil {
		return execProgressMsg{step: execStepCert, err: fmt.Errorf("writing CA cert: %w", err)}
	}
	if err := cert.WritePEM(infra.RootCAKey, caPair.KeyPEM); err != nil {
		return execProgressMsg{step: execStepCert, err: fmt.Errorf("writing CA key: %w", err)}
	}

	wildcard, err := ca.GenerateWildcard(m.session.domain)
	if err != nil {
		return execProgressMsg{step: execStepCert, err: fmt.Errorf("wildcard cert: %w", err)}
	}
	if err := cert.WritePEM(infra.WildcardCert, wildcard.CertPEM); err != nil {
		return execProgressMsg{step: execStepCert, err: fmt.Errorf("writing wildcard cert: %w", err)}
	}
	if err := cert.WritePEM(infra.WildcardKey, wildcard.KeyPEM); err != nil {
		return execProgressMsg{step: execStepCert, err: fmt.Errorf("writing wildcard key: %w", err)}
	}

	return execProgressMsg{step: execStepCert, message: "Generated TLS certificates"}
}

func (m model) doEnvStep() tea.Msg {
	result, err := env.Generate(env.Config{
		BaseDomain: m.session.domain,
		EnvType:    m.session.envType,
	})
	if err != nil {
		return execProgressMsg{step: execStepEnv, err: fmt.Errorf("env generation: %w", err)}
	}

	if err := os.WriteFile(infra.EnvFile, result.Content, 0644); err != nil {
		return execProgressMsg{step: execStepEnv, err: fmt.Errorf("writing .env: %w", err)}
	}

	return execProgressMsg{step: execStepEnv, message: "Created .env file"}
}

func (m model) doNetworkStep() tea.Msg {
	if err := infra.EnsureNetwork(infra.NetworkName); err != nil {
		return execProgressMsg{step: execStepNetwork, err: fmt.Errorf("docker network: %w", err)}
	}
	return execProgressMsg{step: execStepNetwork, message: "Ensured Docker network 'proxy'"}
}

func (m model) View() string {
	switch m.step {
	case stepWelcome:
		return m.welcomeView()
	case stepDomain:
		return m.domainView()
	case stepEnvironment:
		return m.envView()
	case stepBackup:
		return m.backupView()
	case stepExecuting:
		return m.executingView()
	case stepSummary:
		return m.summaryView()
	}
	return ""
}

func (m model) welcomeView() string {
	var b strings.Builder
	b.WriteString(headerStyle.Render("╔══════════════════════════════════════╗"))
	b.WriteString("\n")
	b.WriteString(headerStyle.Render("║          ctl  v0.2.0            ║"))
	b.WriteString("\n")
	b.WriteString(headerStyle.Render("╚══════════════════════════════════════╝"))
	b.WriteString("\n\n")
	b.WriteString(infoStyle.Render("Configure your SaaS infrastructure"))
	b.WriteString("\n\n")
	b.WriteString(subtleStyle.Render("Press Enter to begin"))
	return b.String()
}

func (m model) domainView() string {
	var b strings.Builder
	b.WriteString(headerStyle.Render("Base Domain"))
	b.WriteString("\n\n")
	b.WriteString("Enter your base domain:\n")
	b.WriteString(m.domainInput.View())
	b.WriteString("\n\n")
	b.WriteString(subtleStyle.Render("Enter = confirm"))
	return b.String()
}

func (m model) envView() string {
	var b strings.Builder
	b.WriteString(headerStyle.Render("Environment"))
	b.WriteString("\n\n")
	b.WriteString("Select environment:\n\n")
	for i, env := range m.envTypes {
		cursor := "  "
		prefix := "○"
		if i == m.envCursor {
			cursor = "▸ "
			prefix = "●"
		}
		line := fmt.Sprintf("%s%s %s", cursor, prefix, env)
		if i == m.envCursor {
			b.WriteString(highlightStyle.Render(line))
		} else {
			b.WriteString(line)
		}
		b.WriteString("\n")
	}
	b.WriteString("\n")
	b.WriteString(subtleStyle.Render("↑↓ = navigate  Enter = confirm"))
	return b.String()
}

func (m model) backupView() string {
	var b strings.Builder
	b.WriteString(headerStyle.Render("Backup"))
	b.WriteString("\n\n")

	files := []string{infra.EnvFile, infra.WildcardCert, infra.WildcardKey}
	var found bool
	for _, f := range files {
		if backup.FileExists(f) {
			b.WriteString(successStyle.Render("✓ found: " + f))
			b.WriteString("\n")
			found = true
		}
	}
	if !found {
		b.WriteString(infoStyle.Render("No existing files found"))
		b.WriteString("\n")
	}

	b.WriteString("\n")
	choice := "No"
	if m.session.doBackup {
		choice = "Yes"
	}
	b.WriteString(fmt.Sprintf("Create backups before overwriting? [%s]\n", highlightStyle.Render(choice)))
	b.WriteString("\n")
	b.WriteString(subtleStyle.Render("← → = toggle  Enter = confirm"))
	return b.String()
}

func (m model) executingView() string {
	var b strings.Builder
	b.WriteString("\n")
	b.WriteString(fmt.Sprintf("%s %s\n", m.spin.View(), infoStyle.Render("Setting up your environment...")))
	b.WriteString("\n")
	for _, p := range m.progress {
		b.WriteString(successStyle.Render("✓ " + p))
		b.WriteString("\n")
	}
	return b.String()
}

func (m model) summaryView() string {
	var b strings.Builder
	if m.err != nil {
		b.WriteString(errorStyle.Render("✗ Setup failed"))
		b.WriteString("\n\n")
		b.WriteString(errorStyle.Render(m.err.Error()))
		b.WriteString("\n\n")
		b.WriteString(subtleStyle.Render("Press Enter to exit"))
		return b.String()
	}

	b.WriteString(successStyle.Render("✓ Setup complete!"))
	b.WriteString("\n\n")

	b.WriteString(fmt.Sprintf("%-15s %s\n", "Environment:", m.session.envType))
	b.WriteString(fmt.Sprintf("%-15s %s\n", "Domain:", m.session.domain))
	b.WriteString(fmt.Sprintf("%-15s infra/.env\n", "Env file:"))
	b.WriteString("\n")

	b.WriteString(headerStyle.Render("Services"))
	b.WriteString("\n\n")

	authHost := "auth." + m.session.domain
	appHost := "app." + m.session.domain
	apiHost := "api." + m.session.domain
	traefikHost := "traefik." + m.session.domain

	if m.session.envType == "dev" || m.session.envType == "staging" {
		b.WriteString(fmt.Sprintf("  Traefik:  https://%s:8080\n", traefikHost))
	} else {
		b.WriteString(fmt.Sprintf("  Traefik:  https://%s:8080\n", traefikHost))
	}
	b.WriteString(fmt.Sprintf("  Keycloak: https://%s\n", authHost))
	b.WriteString(fmt.Sprintf("  App:      https://%s\n", appHost))
	b.WriteString(fmt.Sprintf("  API:      https://%s\n", apiHost))
	b.WriteString("\n")

	b.WriteString(headerStyle.Render("Next steps"))
	b.WriteString("\n\n")
	b.WriteString("  1. Trust the CA (optional):\n")
	b.WriteString(fmt.Sprintf("     sudo cp %s /usr/local/share/ca-certificates/ && sudo update-ca-certificates\n", infra.RootCACert))
	b.WriteString("  2. Start the stack:\n")
	b.WriteString("     ./ctl up\n")
	b.WriteString("\n")
	b.WriteString(subtleStyle.Render("Press Enter to exit"))
	return b.String()
}
