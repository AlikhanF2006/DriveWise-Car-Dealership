const test = require('node:test');
const assert = require('node:assert/strict');
const app = require('./index');
const http = require('node:http');

async function request(path) {
  const server = http.createServer(app);
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  try {
    const address = server.address();
    const response = await fetch(`http://127.0.0.1:${address.port}${path}`);
    return {status: response.status, data: await response.json()};
  } finally {await new Promise(resolve => server.close(resolve));}
}
test('lists dealerships', async () => {
  const {status, data} = await request('/api/dealerships');
  assert.equal(status, 200);
  assert.ok(data.dealerships.length > 0);
});
test('filters Kansas dealerships', async () => {
  const {data} = await request('/api/dealerships/state/KS');
  assert.ok(data.dealerships.every(d => d.state === 'KS'));
});
test('returns reviews', async () => {
  const {data} = await request('/api/dealerships/1/reviews');
  assert.ok(data.reviews.length >= 1);
});
