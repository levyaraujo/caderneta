# Use the official PostgreSQL image from the Docker Hub
FROM postgres:16-alpine

# Set environment variables for PostgreSQL
ENV POSTGRES_USER=caderneta
ENV POSTGRES_PASSWORD=senhasecreta
ENV POSTGRES_DB=

# Expose the default PostgreSQL port
EXPOSE 5432

# Add a health check to ensure the database is ready
HEALTHCHECK --interval=10s --timeout=5s --retries=5 \
  CMD pg_isready -U $POSTGRES_USER -d $POSTGRES_DB || exit 1