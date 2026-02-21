# Rice Bikes

## Running

To start the web server:

```
docker compose up
```

To remove the related containers and volumes after you're done, run:

```
docker compose down -v
```

## Testing

To run tests:

```
docker compose exec web python -m pytest
```

This command should be run when the web server and database containers are already running (i.e.
after `docker compose up` is run).

## Design

The backend took precedence over the frontend in terms of design for this project, so I will talk
mostly about that.

Claude was used to generate basic front end styling.

Tech stack:

- **Python**: Flask backend, 3 dependencies (including Flask)
- **PostgresSQL database**
- **Frontend**: pure HTML + CSS + JS, no dependencies

The main challenge of this was to use the existing specification from the "Rice Bikes Take-Home
Assignment" document and adapt it into what I thought would be the most robust design decisions.
As such, I will first go through the point where I deviated from the specifications of the document:

I used JSON strings instead of JSON numbers for passing phone number values in the various APIs.
In my opinion, this is safer and causes confusion. For example, how are country code values
specified using a number? As far as I know, there is no meaningful interpretation of phone
numbers as integers as opposed to strings.

I will now talk about some of the design decisions I made:

1. I used fixed-point numbers on the backend to ensure full accuracy when doing arithmetic with
   money values. With the current state of the project, there is no strict need for this (because
   floating point stringification uses the [shortest round-trippable form](https://github.com/ulfjack/ryu?tab=readme-ov-file#ryu))
2. I only had three run-time dependencies on the backend: [Flask](https://flask.palletsprojects.com/en/stable/),
   [psycogpg](https://www.psycopg.org/), and [JSONSchema](https://github.com/python-jsonschema/jsonschema).
   I believe that all dependencies in a project should have good justification; too much outside
   code can cause safety and maintainability issues. That said, I even felt slightly uncomfortable
   including JSONSchema. Although it is a popular, maintained project in the Python community, I
   would nonetheless replace it with a custom version if I were to continue working on this project.
   It is only a recursive type checker, which is not that difficult to write by hand.
3. I did not use a full ORM and instead wrote SQL by hand. As I wanted to focus on robustness, I
   did not feel comfortable including an ORM when I admittedly have not worked with one before.
   This is something that I would try to include in the project if I were to continue working on it.
   However, I have a lot of experience with SQL drivers (I've even written my own type-safe SQLite
   driver in Zig!), so I am confident in my ability to write safe SQL queries.
4. Integration testing is done with `pytest`. All API end points are tested, with edge cases included.
5. Flask best-practices (application factories, blueprints) were used to ensure long-term maintainability
   and also helped with fixture testing. The DB username and passwords passed via environment variables.
6. Documentation written used when necessary.
7. All backend code is type safe (type-checked with `mypy` version 1.19.1)
8. I generally try to stay away from front end dependencies, including frameworks, because they have a
   high chance of breaking, having safety vulnerabilities, and causing maintainability headaches. For
   a project requiring a complicated front end, I would consider using React or Svelte. Native web
   components generally can get the job done pretty well, though.

Another note is that I saw lots of opportunities for network optimizations (preloading much of the
information is possible), but I stayed away from that to stay in accordance with the take home
assignment document.

## Features

- All features in the document requested
- The ability to create and delete transactions on the frontend and on the backend
- Various table niceities
- Front end doesn't look half-bad (thanks Claude)
