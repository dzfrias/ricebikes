# Rice Bikes

## Running

Start the web server:

```
docker compose up
```

## Testing

Run tests:

```
docker compose exec web python -m pytest
```

This command should be run when the web server and database containers are already running (i.e.
after `docker compose up` is run).

## Design

TODO
