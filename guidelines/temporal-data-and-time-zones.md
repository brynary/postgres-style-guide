# Temporal Data and Time Zones

## Rule

Use `timestamptz` for all timestamps and `date` for calendar dates; model validity periods as range types with half-open `[)` bounds and enforce non-overlap with PG18 temporal constraints.

## Why

`timestamptz` stores an unambiguous instant and renders in the session's zone; plain `timestamp` is a wall-clock reading with no zone, a standing invitation to double-conversion bugs. Ranges make period logic one value with real operators instead of hand-rolled column-pair comparisons.

## Do

- Use `timestamptz` for every point-in-time column (`created_at`, `paid_at`, `expires_at`).
- Use `date` for calendar concepts with no time component (`due_on`, `birth_date`).
- Use `interval` for durations only when the duration itself is the data; otherwise store the two instants.
- Use `tstzrange` or `daterange` with `[)` bounds for validity periods instead of start/end column pairs.
- Enforce non-overlap declaratively: `UNIQUE (key, period WITHOUT OVERLAPS)` on the range column (PG18).
- Install `btree_gist` (`CREATE EXTENSION btree_gist;`, in its own migration) before the first constraint that mixes a scalar key with a range: GiST has no default operator class for scalar types like `uuid`, so both `WITHOUT OVERLAPS` constraints and `EXCLUDE USING gist` fail without it.
- Pass ISO 8601 strings when writing timestamps from SQL (`'2026-07-03T14:00:00Z'`).
- Compare and bucket in SQL with `date_trunc` and range operators (`&&`, `@>`), not string manipulation.

## Avoid

- Do not use `timestamp without time zone` for instants.
- Do not store epoch seconds in numeric columns or timestamps as text.
- Do not model periods as `starts_at`/`ends_at` pairs; nothing stops `starts_at > ends_at`, and overlap checks become bug-prone inequalities.
- Do not use inclusive `[]` range bounds for continuous time; adjacent periods will overlap at the boundary.
- Do not enforce overlap rules with triggers or application checks when a temporal constraint can state them.

## Example

```sql
-- Requires btree_gist for the scalar room_id key part.
CREATE TABLE room_bookings (
  id uuid DEFAULT uuidv7() PRIMARY KEY,
  room_id uuid NOT NULL REFERENCES rooms (id) ON DELETE RESTRICT,
  booked_during tstzrange NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  -- No two bookings for the same room may overlap (PG18):
  CONSTRAINT room_bookings_room_id_booked_during_key
    UNIQUE (room_id, booked_during WITHOUT OVERLAPS)
);

-- Find bookings active right now:
SELECT rb.id
FROM room_bookings rb
WHERE rb.booked_during @> now();
```

## Version Notes

- `WITHOUT OVERLAPS` and temporal `PERIOD` foreign keys require PostgreSQL 18. On older targets, use an exclusion constraint: `EXCLUDE USING gist (room_id WITH =, booked_during WITH &&)`. The `btree_gist` requirement applies to both forms.

## Exceptions

- Future wall-clock events whose UTC offset may change under timezone-rule updates (appointments, scheduled local times): store the local time and the zone name (`text`), with a comment; convert at read time.
- Analytical rollup tables may store pre-truncated `date` buckets even for instant-derived data.
