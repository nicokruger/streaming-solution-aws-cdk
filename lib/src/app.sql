CREATE OR REPLACE STREAM "DESTINATION_SQL_STREAM" (
  "bankId" varchar(256),
  "lastHourSum" double,
  "lastHourTotal" double,
  "lastFiveMinutes" double,
  "lastThreeSum" double
);
CREATE OR REPLACE PUMP "STREAM_PUMP" AS INSERT INTO "DESTINATION_SQL_STREAM"
SELECT STREAM
  "bankId",
  sum("transaction") OVER lastHour as lastHourSum,
  count(*) OVER lastHour as lastHourTotal,
  count(*) OVER lastFiveMinutes as lastFiveMinutes,
  sum("transaction") OVER lastThree as lastThreeSum
FROM "SOURCE_SQL_STREAM_001"
WINDOW
  lastHour AS (RANGE INTERVAL '1' HOUR PRECEDING),
  lastThree AS (ROWS 3 PRECEDING),
  lastFiveMinutes AS (RANGE INTERVAL '5' MINUTE PRECEDING),
  lastZeroRows AS (ROWS CURRENT ROW),
  lastZeroSeconds AS (RANGE CURRENT ROW),
  lastTwoSameTicker AS (PARTITION BY "bankId" ROWS 2 PRECEDING),
  lastHourSameTicker AS (PARTITION BY "bankId" RANGE INTERVAL '1' HOUR PRECEDING)

