# Deployment Guide for Streamlit Cloud

## Prerequisites
- GitHub account
- All API keys ready (OpenAI, Pinecone, OMDb)

## Environment Variables Required

When deploying to Streamlit Cloud, add these secrets in the app settings:

```toml
OPENAI_API_KEY = "your-openai-api-key"
PINECONE_API = "your-pinecone-api-key"
INDEX_NAME = "movie-recommendation"
NAMESPACE = "namespace_until_1990"
EMBEDDING_MODEL = "text-embedding-3-small"
SQLITE_DB_PATH = "data/movies.db"
OMDB_API_KEY = "your-omdb-api-key"
```

## Deployment Steps

### 1. Push to GitHub
Ensure all changes are committed and pushed to your GitHub repository:
```bash
git add .
git commit -m "Prepare for Streamlit Cloud deployment"
git push origin interface
```

### 2. Deploy on Streamlit Cloud
1. Go to https://share.streamlit.io
2. Sign in with your GitHub account
3. Click "New app"
4. Select your repository: `your-username/movie-recommendation`
5. Select branch: `interface` (or `main`)
6. Set main file path: `app.py`
7. Click "Advanced settings"
8. Add the environment variables listed above in the "Secrets" section
9. Click "Deploy"

### 3. Wait for Deployment
- First deployment takes 5-10 minutes (196MB database needs to be uploaded)
- Streamlit Cloud will install dependencies from requirements.txt
- Watch the logs for any errors

### 4. Test Your App
- Once deployed, you'll get a URL like: `https://your-app-name.streamlit.app`
- Test movie search and recommendations
- Verify posters and IMDb links work

## Troubleshooting

### Database not found
- Ensure `data/movies.db` is in your git repository
- Check `.gitignore` allows the database file

### Module import errors
- Check `requirements.txt` has all dependencies with versions
- Streamlit Cloud uses Python 3.9+ by default

### API key errors
- Double-check all secrets are entered correctly in Streamlit Cloud
- No quotes needed around secret values in Streamlit Cloud UI

### Memory issues
- 196MB database + loaded models may hit free tier limits
- Consider upgrading to Streamlit Cloud Pro if needed

## File Checklist
- ✅ `app.py` - Main application
- ✅ `main.py` - Recommendation engine
- ✅ `requirements.txt` - Dependencies with versions
- ✅ `.streamlit/config.toml` - Streamlit configuration
- ✅ `data/movies.db` - SQLite database (196MB)
- ✅ `.gitignore` - Properly configured to include database
- ✅ Environment variables documented

## Notes
- The database file is 196MB - first push to GitHub will take time
- Free Streamlit Cloud has resource limits (1GB RAM)
- App goes to sleep after inactivity, wakes up on first request
