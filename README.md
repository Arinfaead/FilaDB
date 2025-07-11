# FilaDB - 3D Printing Asset Management

A self-hosted application that centralizes 3D printing assets (files & materials) for teams.

## Features

- **Centralized File Management**: Upload and manage .3mf, .gcode & .stl files with version history
- **Multi-User Access**: Email/password authentication with role-based access (admin, editor, viewer)
- **Filament Management**: Integration with SpoolmanDB for comprehensive filament database
- **Inventory Tracking**: Track spool inventory with automatic weight calculations
- **Modern UI**: Clean, responsive web interface built with vanilla HTML5/CSS3/JavaScript

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Git

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd filadb
```

2. Start the application:
```bash
docker-compose up -d
```

3. Access the application at `http://localhost:8000`

4. Login with default admin credentials:
   - Email: `admin@example.com`
   - Password: `admin123`

## Architecture

### Backend
- **Framework**: FastAPI with Python 3.12
- **Database**: PostgreSQL 16 with SQLModel ORM
- **Authentication**: JWT tokens with role-based access control
- **File Storage**: Local filesystem (S3-ready architecture)

### Frontend
- **Technology**: Pure HTML5, CSS3, and ES6 JavaScript
- **Architecture**: Single-page application with modular components
- **Styling**: Responsive design with CSS Grid and Flexbox

## API Documentation

Once running, visit `http://localhost:8000/docs` for interactive API documentation.

## Development

### Local Development Setup

1. Install Python dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Set up database:
```bash
# Start PostgreSQL (via Docker)
docker run -d --name filadb-postgres -e POSTGRES_DB=filadb -e POSTGRES_USER=filadb -e POSTGRES_PASSWORD=filadb_password -p 5432:5432 postgres:16

# Create admin user
python -m app.cli admin@example.com admin123
```

3. Start development server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Environment Variables

Create a `.env` file in the root directory to customize settings:

```env
DATABASE_URL=postgresql://filadb:filadb_password@db:5432/filadb
SECRET_KEY=your-secret-key-here
UPLOAD_DIR=/app/uploads
SPOOLMANDB_URL=https://donkie.github.io/SpoolmanDB/filaments.json
```

## License

This project is licensed under the MIT License.
