#!/usr/bin/env bash
set -euo pipefail

PORT=${PORT:-5000}
LOG=$(mktemp -t assetly_test.XXXXXX.log)
PIDFILE=$(mktemp -t assetly_test.XXXXXX.pid)
TMPRESP=$(mktemp -t assetly_resp.XXXXXX.json)

echo "Starting app on port $PORT (log: $LOG)"
PORT=$PORT python run.py >"$LOG" 2>&1 &
echo $! > "$PIDFILE"

timeout=30
i=0
until curl -sSf "http://127.0.0.1:$PORT/openapi.yaml" > /dev/null; do
  i=$((i+1))
  if [ $i -ge $timeout ]; then
    echo "ERROR: app did not become ready within $timeout seconds. Last log lines:"
    tail -n 200 "$LOG" || true
    kill "$(cat $PIDFILE)" 2>/dev/null || true
    rm -f "$PIDFILE" "$TMPRESP"
    exit 1
  fi
  sleep 1
done

echo "App is up — running endpoint tests..."

BASE="http://127.0.0.1:$PORT"
set +e

echo "1) GET /api/assets"
curl -sS -o /dev/null -w "%{http_code}\n" "$BASE/api/assets"

echo "2) POST /api/assets (create)"
CREATE_PAYLOAD='{"symbol":"TEST123","name":"Test Asset","asset_type":"equity","currency":"USD"}'
HTTP_CODE=$(curl -s -o "$TMPRESP" -w "%{http_code}" -X POST -H "Content-Type: application/json" -d "$CREATE_PAYLOAD" "$BASE/api/assets")
echo "status: $HTTP_CODE"
CREATED_ID=""
if [ "$HTTP_CODE" = "201" ] || [ "$HTTP_CODE" = "200" ]; then
  CREATED_ID=$(python - <<PY
import sys,json
try:
    j=json.load(open('$TMPRESP'))
    # common response shapes: {id:...} or the full asset
    if isinstance(j, dict):
        if 'id' in j:
            print(j['id'])
        elif 'asset' in j and isinstance(j['asset'], dict) and 'id' in j['asset']:
            print(j['asset']['id'])
        else:
            # try to find an integer id in dict values
            for v in j.values():
                if isinstance(v, int):
                    print(v)
                    break
except Exception:
    pass
PY
)
  CREATED_ID=$(echo "$CREATED_ID" | tr -d '\n')
  echo "created id: $CREATED_ID"
else
  echo "Create failed, response body:" && cat "$TMPRESP" || true
fi

if [ -n "$CREATED_ID" ]; then
  echo "3) GET /api/assets/$CREATED_ID"
  curl -sS -o /dev/null -w "%{http_code}\n" "$BASE/api/assets/$CREATED_ID"

  echo "4) PUT /api/assets/$CREATED_ID (update)"
  # send required fields for update
  UPDATE_PAYLOAD='{"symbol":"TEST123","name":"Test Asset Updated","asset_type":"equity","currency":"USD"}'
  curl -s -o /dev/null -w "status: %{http_code}\n" -X PUT -H "Content-Type: application/json" -d "$UPDATE_PAYLOAD" "$BASE/api/assets/$CREATED_ID"

  echo "5) POST /api/assets/$CREATED_ID/sync"
  curl -s -o /dev/null -w "status: %{http_code}\n" -X POST "$BASE/api/assets/$CREATED_ID/sync"

  echo "6) DELETE /api/assets/$CREATED_ID"
  curl -s -o /dev/null -w "status: %{http_code}\n" -X DELETE "$BASE/api/assets/$CREATED_ID"
fi

set -e

echo "Checking python bytecode and syntax..."
python -m compileall -q . || true

echo "Removing .pyc files and __pycache__ directories..."
find . -name '*.pyc' -delete || true
find . -type d -name '__pycache__' -exec rm -rf {} + || true

echo "Stopping app (pid $(cat $PIDFILE))"
kill "$(cat $PIDFILE)" 2>/dev/null || true
rm -f "$PIDFILE" "$TMPRESP"

echo "Test and cleanup finished. Log file: $LOG (kept for inspection)"
echo "If everything passed, you can remove the log with: rm $LOG"

exit 0
