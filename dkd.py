# version: '3.8'

services:


  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  web:
      build: .
      # Tell Docker to run our new script
      command: sh entrypoint.sh
      volumes:
        - .:/app
      ports:
        - "8000:8000"
      env_file:           # <--- Make sure this is here!
      - .env
      depends_on:
        - redis

volumes:
  postgres_data: