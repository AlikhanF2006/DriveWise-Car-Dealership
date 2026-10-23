/** Dealership microservice. Set MONGODB_URI for persistent MongoDB; otherwise
 * endpoints serve clearly labeled fictional in-memory development data.
 */
const express = require('express');
const {MongoClient} = require('mongodb');
const app = express();
app.use(express.json());
const samples = [
  {id: 1, name: 'DriveWise Kansas City', city: 'Kansas City', state: 'KS', address: '100 Demo Plaza'},
  {id: 2, name: 'Sunflower Auto Center', city: 'Wichita', state: 'KS', address: '18 Sample Avenue'},
  {id: 3, name: 'Prairie Motor Group', city: 'Topeka', state: 'KS', address: '45 Training Boulevard'},
  {id: 4, name: 'Rocky Mountain Cars', city: 'Denver', state: 'CO', address: '300 Sample Road'},
  {id: 5, name: 'Lone Star Auto Gallery', city: 'Dallas', state: 'TX', address: '220 Example Street'},
];
const sampleReviews = [
  {id: 1, dealer_id: 1, user: 'demo', rating: 5, review: 'Fantastic services and great staff.'},
  {id: 2, dealer_id: 2, user: 'demo', rating: 4, review: 'Helpful service and a smooth experience.'},
];
let dealersCollection = null;
let reviewsCollection = null;

async function listDealers() {
  if (!dealersCollection) return samples;
  const data = await dealersCollection.find({}).limit(1000).toArray();
  return data.map(({_id, ...item}) => item);
}
async function listReviews() {
  if (!reviewsCollection) return sampleReviews;
  const data = await reviewsCollection.find({}).limit(1000).toArray();
  return data.map(({_id, ...item}) => item);
}
const handle = fn => (req, res) => Promise.resolve(fn(req, res)).catch(err => {
  console.error(err);
  res.status(500).json({error: 'Database request failed'});
});
app.get('/', (_req, res) => res.json({app: 'DriveWise Express Dealer API', storage: dealersCollection ? 'mongodb' : 'fictional-sample-data'}));
app.get('/api/dealerships', handle(async (_req, res) => res.json({dealerships: await listDealers()})));
app.get('/api/dealerships/state/:state', handle(async (req, res) => {
  res.json({state: req.params.state.toUpperCase(), dealerships: (await listDealers()).filter(x => x.state.toUpperCase() === req.params.state.toUpperCase())});
}));
app.get('/api/dealerships/:id/reviews', handle(async (req, res) => {
  const id = Number(req.params.id);
  res.json({dealer_id: id, reviews: (await listReviews()).filter(r => r.dealer_id === id)});
}));
app.get('/api/dealerships/:id', handle(async (req, res) => {
  const dealer = (await listDealers()).find(x => x.id === Number(req.params.id));
  if (!dealer) return res.status(404).json({error: 'Dealer not found'});
  return res.json(dealer);
}));
async function start() {
  if (process.env.MONGODB_URI) {
    const client = new MongoClient(process.env.MONGODB_URI, {serverSelectionTimeoutMS: 5000});
    await client.connect();
    const database = client.db(process.env.MONGODB_DB || 'drivewise');
    dealersCollection = database.collection('dealers');
    reviewsCollection = database.collection('reviews');
    if (process.env.SEED_MONGO === '1') {
      if (!await dealersCollection.countDocuments()) await dealersCollection.insertMany(samples);
      if (!await reviewsCollection.countDocuments()) await reviewsCollection.insertMany(sampleReviews);
    }
    console.log('MongoDB connected.');
  } else console.log('Using fictional sample-data fallback; set MONGODB_URI for MongoDB.');
  app.listen(process.env.PORT || 3001, () => console.log('Dealer API listening at http://127.0.0.1:' + (process.env.PORT || 3001)));
}
if (require.main === module) start().catch(err => {console.error(err.message); process.exit(1);});
module.exports = app;
