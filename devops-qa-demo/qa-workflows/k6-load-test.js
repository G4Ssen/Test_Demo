import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  // Simulate ramp-up, steady state, and ramp-down
  stages: [
    { duration: '10s', target: 20 }, // ramp up to 20 users
    { duration: '30s', target: 20 }, // stay at 20 users
    { duration: '10s', target: 0 },  // ramp down
  ],
  thresholds: {
    // 95% of requests must complete below 500ms
    http_req_duration: ['p(95)<500'],
    // Less than 1% of requests should fail
    http_req_failed: ['rate<0.01'],
  },
};

export default function () {
  // In the demo, we point to our local Forgejo instance
  const res = http.get('http://git.localhost');
  
  check(res, {
    'status is 200': (r) => r.status === 200,
    'body contains Forgejo': (r) => r.body.includes('Forgejo'),
  });
  
  sleep(1);
}
