# FilaDB - Filament Management System

FilaDB is a comprehensive filament management system for 3D printing enthusiasts and workshops, inspired by Spoolman. It provides a web-based interface for managing filaments, spools, printers, and print jobs with multi-user support and NFC integration capabilities.

## Features

### Core Features
- **Filament Management**: Track filament types, manufacturers, materials, and individual spools
- **Multi-User System**: User authentication with role-based access control
- **Multi-Printer Support**: Manage multiple 3D printers simultaneously
- **Dark Mode UI**: Modern dark theme inspired by Spoolman
- **REST API**: Full REST API for external integrations

### Planned Features
- **NFC Integration**: Track spools using NFC tags (Android & iOS compatible)
- **Bambu Lab Integration**: Connect with Bambu Lab printers via Bambu Connect API
- **SpoolmanDB Integration**: Community-supported filament database
- **QR Code Labels**: Generate and print QR code labels for spools
- **Activity Logging**: Track all user actions and changes

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **PostgreSQL**: Robust database for data storage
- **SQLAlchemy**: ORM for database operations
- **JWT Authentication**: Secure token-based authentication
- **Docker**: Containerized deployment

### Frontend
- **React**: Modern JavaScript UI framework
- **Tailwind CSS**: Utility-first CSS framework
- **React Query**: Data fetching and caching
- **React Router**: Client-side routing
- **Axios**: HTTP client for API calls

## Installation

### Prerequisites
- Docker and Docker Compose
- Git

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd filadb
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start the application**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Web Interface: http://localhost
   - API Documentation: http://localhost/docs
   - API Alternative Docs: http://localhost/redoc

### Default Credentials
The system will create a default admin user on first startup:
- **Username**: admin
- **Password**: admin123
- **Email**: admin@filadb.local

**⚠️ Important**: Change the default password immediately after first login!

## Configuration

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# Database Configuration
POSTGRES_DB=filadb
POSTGRES_USER=filadb
POSTGRES_PASSWORD=your_secure_password
DATABASE_URL=postgresql+asyncpg://filadb:your_secure_password@db:5432/filadb

# Security
SECRET_KEY=your_very_secure_secret_key_here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Settings
CORS_ORIGINS=["http://localhost", "http://localhost:3000"]

# Optional: External Services
# BAMBU_LAB_API_KEY=your_bambu_lab_api_key
# SPOOLMAN_DB_URL=https://api.spoolman.db
```

### Docker Compose Services

The application consists of several services:

- **nginx**: Reverse proxy and load balancer
- **frontend**: React application (port 3000)
- **backend**: FastAPI application (port 8000)
- **db**: PostgreSQL database (port 5432)

## API Documentation

The API is fully documented and available at:
- Swagger UI: http://localhost/docs
- ReDoc: http://localhost/redoc

### Authentication

All API endpoints (except login) require authentication using JWT tokens:

```bash
# Login to get token
curl -X POST "http://localhost/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"

# Use token in subsequent requests
curl -X GET "http://localhost/api/users/me" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Key Endpoints

- **Authentication**: `/api/auth/`
- **Users**: `/api/users/`
- **Manufacturers**: `/api/manufacturers/`
- **Materials**: `/api/materials/`
- **Filaments**: `/api/filaments/`
- **Spools**: `/api/spools/`
- **Printers**: `/api/printers/`

## Development

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd frontend
npm install
npm start
```

### Database Migrations

The application automatically creates database tables on startup. For manual database operations:

```bash
# Access database
docker-compose exec db psql -U filadb -d filadb

# View logs
docker-compose logs backend
docker-compose logs frontend
```

## Usage

### Managing Manufacturers
1. Navigate to "Manufacturers" in the sidebar
2. Click "Add Manufacturer" to create new entries
3. Edit or delete existing manufacturers as needed

### Managing Materials
1. Go to "Materials" section
2. Add material types (PLA, ABS, PETG, etc.) with properties
3. Set density, temperature ranges, and custom properties

### Managing Filaments
1. Visit "Filaments" page
2. Create filament entries linking manufacturers and materials
3. Specify colors, weights, diameters, and settings

### Managing Spools
1. Access "Spools" section
2. Add individual spool instances
3. Track weight, remaining amount, location, and custom fields
4. Assign spools to printers when in use

### Managing Printers
1. Go to "Printers" section
2. Add your 3D printers with details
3. Monitor printer status and assigned spools

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check if PostgreSQL container is running: `docker-compose ps`
   - Verify database credentials in `.env` file
   - Check logs: `docker-compose logs db`

2. **Frontend Not Loading**
   - Ensure all containers are running: `docker-compose ps`
   - Check frontend logs: `docker-compose logs frontend`
   - Verify nginx configuration

3. **API Authentication Issues**
   - Check if JWT secret key is properly set
   - Verify token expiration settings
   - Check backend logs: `docker-compose logs backend`

### Logs and Debugging

```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs db
docker-compose logs nginx

# Follow logs in real-time
docker-compose logs -f backend
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Submit a pull request with a clear description

### Development Guidelines
- Follow PEP 8 for Python code
- Use ESLint and Prettier for JavaScript code
- Write tests for new features
- Update documentation as needed

## Roadmap

### Version 1.1
- [ ] NFC tag integration
- [ ] QR code label generation
- [ ] Bambu Lab printer integration
- [ ] SpoolmanDB integration

### Version 1.2
- [ ] Mobile companion app
- [ ] Advanced reporting and analytics
- [ ] Inventory management features
- [ ] Multi-language support

### Version 2.0
- [ ] MQTT integration for real-time printer monitoring
- [ ] Advanced user permissions and groups
- [ ] API rate limiting and advanced security
- [ ] Cloud deployment options

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please:
1. Check the troubleshooting section above
2. Search existing GitHub issues
3. Create a new issue with detailed information
4. Join our community discussions

## Acknowledgments

- Inspired by [Spoolman](https://github.com/Donkie/Spoolman)
- Built with modern web technologies
- Community-driven development
