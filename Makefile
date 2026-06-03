BASE_DOMAIN ?= local.dev
GO_RUN   := go run -C tools/ctl .
GO_BUILD := go build -C tools/ctl -o ../../ctl .

# ── Build ──────────────────────────────────────────────────────────────────────

.PHONY: build
build:
	$(GO_BUILD)

.PHONY: build-linux
build-linux:
	GOOS=linux GOARCH=amd64 $(GO_BUILD)

# ── Setup ──────────────────────────────────────────────────────────────────────

.PHONY: setup
setup:
	$(GO_RUN) setup --domain $(BASE_DOMAIN)

.PHONY: setup-ci
setup-ci:
	$(GO_RUN) setup --domain $(BASE_DOMAIN) --no-interactive

# ── Lifecycle ──────────────────────────────────────────────────────────────────

.PHONY: up
up:
	$(GO_RUN) up

.PHONY: down
down:
	$(GO_RUN) down

.PHONY: logs
logs:
	$(GO_RUN) logs

.PHONY: status
status:
	$(GO_RUN) status

.PHONY: clean
clean:
	$(GO_RUN) clean

.PHONY: clean-all
clean-all:
	$(GO_RUN) clean --volumes --certs --force

# ── Dev ────────────────────────────────────────────────────────────────────────

.PHONY: dev
dev:
	$(GO_RUN) $(CMD)

.PHONY: run
run: up

.PHONY: restart
restart: down up
