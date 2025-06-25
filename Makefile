.ONESHELL:
.SILENT:
.PHONY: setup download_azd install_pandoc_tex run_local build_local ruff export_reqs test_all type_check bump_dry help
.DEFAULT_TARGET: setup

ROOT_PATH := $(PWD)
APP_PATH := $(ROOT_PATH)/src
APP_START := src.app:main
REQS_FILE := $(ROOT_PATH)/requirements.txt
TOML_FILE := $(ROOT_PATH)/pyproject.toml
STARTUP_FILE := $(ROOT_PATH)/scripts/startup.sh
VENV_PATH := $(ROOT_PATH)/.venv
LOG_PATH := $(ROOT_PATH)/logs
AZD_URL := https://aka.ms/install-azd.sh

setup:
	echo "Setting up tool chain ..."
	cat /etc/os-release | grep PRETTY_NAME
	pip3 install --no-cache-dir --disable-pip-version-check uv
	uv sync --all-groups
	$(MAKE) -s download_azd
	$(MAKE) -s install_pandoc_tex

download_azd:
	echo "Setting up azd ..."
	if ! which "azd" > /dev/null 2>&1; then
		curl -fsSL "$(AZD_URL)" | bash
	else
		echo "azd already present."
	fi

install_pandoc_tex:
	echo "Setting up pandoc and texlive ..."
	# tools_pkgs="pandoc texlive"
	tools_cmds="pandoc pdflatex"
	tools_to_install=""
	for tool in $$tools_cmds; do
		if $$tool --version >/dev/null 2>&1; then
			echo "$${tool} already installed: $$($$tool --version | head -n 1)"
		else
			tools_to_install="$${tools_to_install} $${tool}"
		fi
	done
	if [ -n "$$tools_to_install" ]; then
		# check if sudo present, assume root otherwise
		if [ -n "$$(sudo --version 2>/dev/null)" ]; then
			SUDO="sudo"
		else
			SUDO=""
		fi
		$$SUDO apt-get update -qq
		# known good: pandoc 2.17.1.1, pdfTeX 3.141592653-2.6-1.40.24
		for tool in $$tools_to_install; do
			# TODO  remove case for indexing $tools_pkgs with $tools_cmds
			case "$$tool" in
				pandoc) tool_to_install="pandoc" ;;
				pdflatex) tool_to_install="texlive" ;;
				*) echo "Unknown tool. Exiting iteration ..." && continue ;;
			esac
			echo "Installing $${tool_to_install} ..."
			$$SUDO apt-get install $$tool_to_install -y -qq 1>/dev/null || \
				{ echo "Failed to install $${tool_to_install}. Exiting ..."; continue; }
			$$tool --version | head -n 1
		done
		$$SUDO apt-get install -f -y -qq
		$$SUDO apt-get autoclean -y -qq
		$$SUDO apt-get autoremove -y -qq
	fi

run_local:
	$(MAKE) -s ruff
	mkdir -p "$(LOG_PATH)"
	SYS_ROOT_PATH="$(ROOT_PATH)" uv run uvicorn $(APP_START) --reload

build_local:
	$(MAKE) -s ruff
	$(MAKE) -s export_reqs
	chmod +x "$(STARTUP_FILE)"
	SYS_ROOT_PATH="$(ROOT_PATH)" VENV_PATH="$(VENV_PATH)" bash -x "$(STARTUP_FILE)"

ruff:
	uv run ruff check --fix
	uv run ruff format

export_reqs:  # Exports packages to requirements.txt
	uv export --format requirements-txt --no-dev > "$(REQS_FILE)"

test_all:
	SYS_ROOT_PATH="$(ROOT_PATH)" uv run pytest --tb=short

type_check:
	uv run mypy src

bump_dry:  # Runs bump-my-version strat=[strat] in dry-mode to show what-if
	if [ -z "$$strat" ];
		then strat="minor";
	fi
	case "$$strat" in \
		"major"|"minor"|"patch") \
			echo "Bumping strategy: '$$strat'"; \
			bump-my-version bump "$$strat" --dry-run --allow-dirty -v; \
			;; \
		*) \
			echo "Invalid strategy: '$$strat'. Exiting ..."; \
			exit 1; \
			;; \
	esac

help:
	# TODO add stackoverflow source
	echo "Usage: make [recipe]"
	echo "Recipes:"
	awk '/^[a-zA-Z0-9_-]+:.*?##/ {
		helpMessage = match($$0, /## (.*)/)
		if (helpMessage) {
			recipe = $$1
			sub(/:/, "", recipe)
			printf "  \033[36m%-20s\033[0m %s\n", recipe, substr($$0, RSTART + 3, RLENGTH)
		}
	}' $(MAKEFILE_LIST)
