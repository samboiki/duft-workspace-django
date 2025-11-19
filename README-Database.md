# PostgreSQL Database Setup

This directory contains a Docker Compose configuration to spin up a PostgreSQL database for the DUFT workspace.

## Database Configuration

The PostgreSQL database is configured with the following credentials:

- **Server**: 127.0.0.1 (localhost)
- **Port**: 5432
- **Username**: postgres
- **Password**: postgres
- **Database**: qe_data

## Quick Start

1. **Start the database**:
   ```bash
   docker-compose up -d postgres
   ```

2. **Stop the database**:
   ```bash
   docker-compose down
   ```

3. **View logs**:
   ```bash
   docker-compose logs postgres
   ```

4. **Connect to the database**:
   ```bash
   # Using psql command line
   docker-compose exec postgres psql -U postgres -d qe_data
   
   # Or connect from your application using the connection string:
   # postgresql://postgres:postgres@127.0.0.1:5432/qe_data
   ```

## Features

- **Persistent Data**: Database data is stored in a Docker volume (`postgres_data`)
- **Health Checks**: Container includes health monitoring
- **Auto-restart**: Container will restart automatically unless manually stopped
- **Initialization Scripts**: Custom SQL scripts can be placed in `init-scripts/` directory

## Database Connection Details for Applications

Use these connection parameters in your applications:

```json
{
  "EPMS_Destination": {
    "type": "PostgreSQL",
    "server": "127.0.0.1",
    "username": "postgres",
    "password": "postgres",
    "port": "5432",
    "database": "qe_data"
  }
}
```

## Troubleshooting

- **Port already in use**: If port 5432 is already in use, change the port mapping in `docker-compose.yml`
- **Permission issues**: Make sure Docker has proper permissions to create volumes
- **Connection refused**: Ensure the container is running with `docker-compose ps`

## Development Notes

- The database will be automatically created when the container starts
- Initial setup scripts are located in the `init-scripts/` directory
- Data persists between container restarts via the `postgres_data` volume