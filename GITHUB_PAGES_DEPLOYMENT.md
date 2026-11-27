# GitHub Pages Deployment

The React frontend is deployable through GitHub Pages.

## Automatic deployment

1. Push the project to the `main` branch on GitHub.
2. Open **Settings > Pages** in the repository.
3. Set **Source** to **GitHub Actions**.
4. Run or wait for the `Deploy React frontend to GitHub Pages` workflow.

The site will be published at:

`https://jithendrava.github.io/DESIGNATHON/`

## Backend requirement

GitHub Pages cannot run FastAPI or Python ML. Deploy the backend to an HTTPS host such as Render, Azure App Service, or Railway.

Then add this repository variable in GitHub:

- Name: `VITE_API_URL`
- Value: `https://YOUR-BACKEND-HOST/api`

Add the GitHub Pages origin to FastAPI CORS:

`https://jithendrava.github.io`

Never place Azure OpenAI API keys in the React project or GitHub Pages variables.

## Local development

```powershell
cd frontend-react
npm install
npm run dev
```

The local Vite proxy sends `/api` requests to `http://127.0.0.1:8000`.
