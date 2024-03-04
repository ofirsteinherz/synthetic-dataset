git-push:
	@read -p "Enter commit message: " message; \
	git status; \
	git add .; \
	git commit -m "$$message"; \
	git push -u origin main;