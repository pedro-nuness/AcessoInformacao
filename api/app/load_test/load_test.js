import http from 'k6/http';
import { check, sleep } from 'k6';
import { Trend, Counter } from 'k6/metrics';
import { uuidv4 } from 'https://jslib.k6.io/k6-utils/1.4.0/index.js';
import { BASE_PAYLOAD } from './load_data.js';

// ================= CONFIG =================
const BASE_URL = 'http://192.168.1.108:8000/processing';

const POLL_INTERVAL = 0.5; // seconds
const POLL_TIMEOUT = 20;   // seconds
const TARGET_STATUS = 'ready';

// ================= METRICS =================
export const postLatency = new Trend('latency_post', true);
export const e2eLatency = new Trend('latency_e2e', true);
export const pollCount = new Trend('poll_count', false);

export const completed = new Counter('completed');
export const failed = new Counter('failed');

// ================= SCENARIO =================
export const options = {
  scenarios: {
    load_test: {
      executor: 'constant-arrival-rate',
      rate: 1000,            // RPS
      timeUnit: '1s',
      duration: '10s',
      preAllocatedVUs: 2000,
      maxVUs: 10000,
    },
  },
  thresholds: {
    latency_post: ['p(95)<2000'],
    latency_e2e: ['p(95)<3000'],
    http_req_failed: ['rate<0.01'],
  },
};


// ================= TEST =================
export default function () {
  const payload = Object.assign({}, BASE_PAYLOAD);
  payload.externalId += uuidv4();
  payload.originalText += ` (${payload.externalId})`;

  const startE2E = Date.now();

  // -------- PHASE 1: POST --------
  const postStart = Date.now();
  const postRes = http.post(
    BASE_URL,
    JSON.stringify(payload),
    { headers: { 'Content-Type': 'application/json' } }
  );

  postLatency.add(Date.now() - postStart);

  if (!check(postRes, { 'POST status 2xx': r => r.status >= 200 && r.status < 300 })) {
    failed.add(1);
    return;
  }

  const body = postRes.json();
  const processingId = body && body.id;

  if (!processingId) {
    failed.add(1);
    return;
  }

  // -------- PHASE 2: POLLING --------
  let polls = 0;
  const pollStart = Date.now();

  while (true) {
    polls++;

    if ((Date.now() - pollStart) / 1000 > POLL_TIMEOUT) {
      failed.add(1);
      return;
    }

    const res = http.get(`${BASE_URL}/${processingId}`);

    if (res.status === 200) {
      const data = res.json();
      const shipment = data && data.shipment;
      const status = shipment && shipment.status;

      if (status === TARGET_STATUS) {
        pollCount.add(polls);
        e2eLatency.add(Date.now() - startE2E);
        completed.add(1);
        return;
      }

      if (status === 'failed' || status === 'error') {
        failed.add(1);
        return;
      }
    } else if (res.status !== 404) {
      failed.add(1);
      return;
    }

    sleep(POLL_INTERVAL);
  }
}
