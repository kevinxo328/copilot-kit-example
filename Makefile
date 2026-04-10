.PHONY: backend frontend dev install clean

backend:
	cd backend && uv run task dev

frontend:
	cd frontend && pnpm dev

dev:
	@python3 scripts/dev.py

install:
	cd backend && uv sync
	cd frontend && pnpm install

clean:
	rm -rf backend/.venv
	rm -rf frontend/node_modules
