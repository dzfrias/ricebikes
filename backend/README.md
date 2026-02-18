docker run --name ricebikes-postgres \
 -e POSTGRES_USER=ricebikes \
 -e POSTGRES_PASSWORD=ricebikes \
 -e POSTGRES_DB=ricebikesdb \
 -p 5432:5432 \
 -d postgres:17
