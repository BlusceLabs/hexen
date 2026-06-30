# 🚀 Hexen Quick Start Guide

## Prerequisites

- Python 3.10+
- Node.js 18+
- npm or pnpm

## Installation

### 1. Clone and Setup Backend

```bash
# Install Python dependencies
pip install -e .

# Or with uv (recommended)
uv pip install -e .

# Copy environment variables
cp .env.example .env

# Edit .env with your configuration (optional - works with defaults)
```

### 2. Setup Frontend

```bash
cd frontend
npm install
# or: pnpm install
```

## Running the Application

### Development Mode

**Terminal 1 - Backend Server:**
```bash
python backend_server.py
# Server runs on http://localhost:8000
```

**Terminal 2 - Frontend Dev Server:**
```bash
cd frontend
npm run dev
# Frontend runs on http://localhost:4321
```

### Access the Application

- **Frontend**: http://localhost:4321
- **Backend API**: http://localhost:8000
- **Backend Docs**: http://localhost:8000/api/docs (if available)

## Features Overview

### Home Page
- **Hero Banner** - Featured trending content
- **Content Carousels** - Trending, Popular Movies, Popular TV, Top Rated
- **Genre Browser** - Quick access to categories

### Video Player
- Custom controls with keyboard shortcuts
- Press `Space` or `K` to play/pause
- Press `F` for fullscreen
- Press `M` to mute/unmute
- Arrow keys for seeking and volume

### Search
- Real-time search as you type
- Keyboard navigation with arrow keys
- Results show movies, TV shows, and people

### Discover
- Filter by genre, year, rating
- Sort by popularity, rating, release date
- Pagination for browsing

## API Usage

### Python API

```python
from hexenapi.backend import Search, Session

# Create session
session = Session()

# Search for content
search = Search(session, query="Inception")
results = await search.get_content_model()

# Get movie details
from hexenapi.backend import ItemDetails
details = ItemDetails(session, detail_path="/movie/inception")
content = await details.get_content()
```

### Backend Server API

```bash
# Search
curl "http://localhost:8000/api/stream/info?q=Inception"

# Get TV episode
curl "http://localhost:8000/api/stream/tv?q=Breaking+Bad&season=1&episode=1"

# Proxy video stream
curl "http://localhost:8000/proxy?url=VIDEO_URL"
```

## Building for Production

### Frontend

```bash
cd frontend
npm run build
npm run preview  # Test production build
```

### Backend

```bash
# The backend is production-ready as-is
python backend_server.py
```

### Deploy with Docker (Coming Soon)

```bash
docker-compose up -d
```

## Configuration

### Environment Variables

Edit `.env` file:

```env
# Backend
HOST=0.0.0.0
PORT=8000

# Frontend
PUBLIC_API_BASE=http://localhost:8000

# Optional: Override API credentials
MOVIEBOX_SECRET_KEY_DEFAULT=your_key
MOVIEBOX_AUTH_TOKEN=your_token
```

## Troubleshooting

### Backend Issues

**Port already in use:**
```bash
python backend_server.py 8001  # Use different port
```

**Import errors:**
```bash
pip install -e .  # Reinstall in development mode
```

### Frontend Issues

**Module not found:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Build errors:**
```bash
npm run check  # Check for TypeScript errors
```

### Common Issues

**CORS errors:**
- Make sure `PUBLIC_API_BASE` in `.env` matches your backend URL
- Backend already has CORS enabled in `backend_server.py`

**Video not playing:**
- Check browser console for errors
- Verify the video URL is accessible
- Try a different video source

## Development Tips

### Code Quality

```bash
# Check Python code
ruff check .
ruff format .

# Check frontend
cd frontend
npm run check
npm run lint
```

### Testing

```bash
# Run Python tests
make test

# Or directly
pytest tests/
```

### Hot Reload

Both backend and frontend support hot reload:
- Backend: Restart `backend_server.py` when needed
- Frontend: Changes auto-reload in dev mode

## Key Files

```
hexen/
├── backend_server.py          # Backend API server
├── .env.example              # Configuration template
├── src/hexenapi/             # Python package
│   └── backend/              # Core API logic
├── frontend/                 # Astro + Svelte frontend
│   ├── src/
│   │   ├── components/       # Reusable components
│   │   ├── pages/           # Routes
│   │   └── layouts/         # Page layouts
│   └── astro.config.mjs     # Astro configuration
└── tests/                   # Test suite
```

## Next Steps

1. **Customize the theme** - Edit `frontend/tailwind.config.mjs`
2. **Add authentication** - Implement user login
3. **Deploy to production** - Use Vercel, Netlify, or Docker
4. **Add more features** - See IMPROVEMENTS_SUMMARY.md for ideas

## Support

- **Documentation**: See README.md and IMPROVEMENTS_SUMMARY.md
- **Issues**: Report bugs via GitHub issues
- **API Docs**: https://hexenapi-docs.netlify.app/

## License

See LICENSE file for details.

---

**Enjoy streaming with Hexen!** 🎬🍿
