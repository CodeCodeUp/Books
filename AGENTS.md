# AGENTS.md

## Purpose
- This file is the primary repo guide for agentic coding agents working in this repository.
- Scope: the entire repo rooted at `Books/`.
- Prefer this file for day-to-day execution rules and `CLAUDE.md` for deeper project context.

## Rule Sources
- `CLAUDE.md`: supplemental architecture, API, and startup notes.
- No Cursor rules were found in `.cursor/rules/` or `.cursorrules`.
- No Copilot rules were found in `.github/copilot-instructions.md`.

## Repository Shape
- `book-recommendation-frontend/`: Vue 3 + Vite + Pinia + Element Plus UI.
- `book-recommendation-backend/`: Spring Boot 3.1 + MyBatis Plus + JWT.
- `recommendation-algorithm-service/`: Flask + pandas + scikit-learn.
- `docker-compose.yml`: optional full-stack local orchestration.

## Architecture Notes
- Frontend owns UI, route guards, client state, and HTTP client wrappers.
- Backend owns auth, validation, persistence, and API aggregation.
- Algorithm service owns recommendation algorithms, caches, and data loading.
- Integrate across services over HTTP only; do not share implementation code directly.
- Start locally in this order: algorithm service -> backend -> frontend.

## Root Commands
```bash
docker-compose up
docker-compose up -d
docker-compose down
docker-compose logs -f
docker-compose logs -f backend
docker-compose restart algorithm-service
```

## Frontend Commands
```bash
cd book-recommendation-frontend
npm install
npm run dev
npm run build
npm run preview
```
- `package.json` only defines `dev`, `build`, and `preview`.
- No repo-configured frontend lint/test command or single-test runner exists.

## Backend Commands
```bash
cd book-recommendation-backend
mvn spring-boot:run
mvn clean package -DskipTests
mvn test
mvn test -Dtest=UserServiceTest
mvn test -Dtest=UserServiceTest#someMethod
java -jar target/book-recommendation-1.0.0.jar
```
- Backend is the only module with a documented test runner.
- `src/test` is currently absent, so single-test commands are future-facing until tests exist.

## Algorithm Service Commands
```bash
cd recommendation-algorithm-service
pip install -r requirements.txt
python app.py
python run_evaluation.py
```
- `tests/` exists but is empty in the current tree.
- Do not assume `pytest`, `ruff`, `black`, or `mypy` are available.

## Tooling Gaps
- Do not claim `npm test`, `npm run lint`, or frontend single-test commands exist; they do not.
- Do not claim `pytest`, `ruff`, `black`, or `mypy` exist; they are not configured.
- Do not claim Maven Checkstyle, SpotBugs, PMD, or Spotless exists; they are not configured.
- Do not rely on README-only start scripts that are missing from the tree.

## Key Paths
- Frontend app entry: `book-recommendation-frontend/src/main.js`.
- Frontend request wrapper: `book-recommendation-frontend/src/utils/request.js`.
- Backend config: `book-recommendation-backend/src/main/resources/application.yml`.
- Algorithm service entry: `recommendation-algorithm-service/app.py`.
- Backend API envelope: `book-recommendation-backend/src/main/java/com/bookrs/recommendation/common/Result.java`.

## Cross-Cutting Coding Rules
- Match local style in touched files; avoid wide formatting-only churn.
- Keep changes service-local unless a contract change truly crosses layers.
- Prefer focused, reversible patches over opportunistic rewrites.
- When adding new behavior, update the owning service first, then dependents.

## Frontend Style
- Use Vue 3 Composition API and `<script setup>` for new components and views.
- Use 2-space indentation in `.js` and Vue `<script>` blocks.
- Existing JS style is no semicolons; keep that unless a formatter is introduced repo-wide.
- Use PascalCase for component filenames and component imports.
- Use camelCase for variables, refs, computed values, and functions.
- Keep page-level logic in `src/views/` and reusable UI in `src/components/`.
- Keep API wrappers in `src/api/*.js`; do not scatter raw `axios` calls through pages.
- Route all HTTP traffic through `src/utils/request.js` so auth/error handling stays centralized.
- Use Pinia for shared session/user state; do not duplicate auth state per view.
- Imports usually follow: Vue/core -> third-party libs/CSS -> local modules/components.
- Wrap async API calls in `try/catch/finally`; use `ElMessage` for user-visible failures.
- Do not leave `console.log` debugging in committed code; clear loading flags in `finally`.

## Backend Style
- Use 4-space indentation and the existing Spring/Lombok brace style.
- Keep controllers thin: parse params, call services, return response envelopes.
- Put business logic in `service/`, not in controllers or mappers.
- Keep persistence concerns in `mapper/` and query wrappers in services.
- Prefer constructor injection via `@RequiredArgsConstructor`.
- Existing API responses use `Result<T>` and `PageResult<T>`; preserve that envelope.
- Existing code often returns entities and `Map<String, Object>`; do not widen that habit.
- For new endpoints, prefer explicit request/response DTOs over more raw `Map` payloads.
- Add `@Operation` and `@Tag` when editing public controllers.
- Avoid returning sensitive fields, especially anything derived from `User.password`.
- Validate null/empty inputs early and return meaningful errors.
- No global `@ControllerAdvice` exists today; do not add more silent exception swallowing.
- Add `@Slf4j` for new business-critical service flows.
- Log external service calls, IDs, paging params, and fallback decisions.
- Never log passwords, JWTs, or secrets.

## Python Algorithm Style
- Use 4-space indentation.
- Use snake_case for functions and variables.
- Favor PEP8 import grouping in new files, but avoid churn-only reorder in old files.
- Keep Flask route handlers thin; push logic into `algorithms/`, `data/`, or `utils/`.
- Maintain the JSON response contract: `success`, `data`, `message`.
- Use logging, not `print`.
- Add helper methods when logic grows; `hybrid.py` is already very large.
- Catch exceptions at API/service boundaries, log context, and return clear failure payloads.
- Do not silently return empty lists or frames without logging why.

## Security And Configuration
- Treat hardcoded DB hosts, passwords, and JWT secrets in the repo as technical debt, not precedent.
- New code must prefer environment variables or external config for secrets.
- Do not commit new real credentials to `README.md`, `.env.example`, `application.yml`, `config.py`, or `docker-compose.yml`.
- Be especially careful with `User` responses; the current entity contains a `password` field.

## Testing Expectations
- Only backend has a documented test invocation today.
- If you add backend tests, keep them runnable with `mvn test -Dtest=ClassName`.
- If needed, Maven Surefire also supports `mvn test -Dtest=ClassName#methodName` for a single method.
- If you add frontend or Python tests, also add the missing scripts/config for stable single-test execution.
- Do not claim tests passed unless you actually ran them.

## Known Gaps
- No `.editorconfig` was found.
- No frontend ESLint/Prettier, backend style plugin, or Python formatter/linter config was found.
- No frontend tests, backend `src/test`, or Python tests were found.
- No CI workflow was found.

## Practical Workflow
- First identify the owning service.
- Then inspect the nearest existing file in that service and copy its local patterns.
- For cross-service changes, update the contract owner first, then dependents.
- Before finishing, run only the commands that are truly configured in the repo.
- If a command is missing, say so explicitly instead of inventing one.
