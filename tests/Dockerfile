# Use the official PostgreSQL image from the Docker Hub
FROM postgres:16-alpine

EXPOSE 5433

# Add a health check to ensure the database is ready
HEALTHCHECK --interval=10s --timeout=5s --retries=5 \
  CMD pg_isready -U $POSTGRES_USER -d $POSTGRES_DB || exit 1