import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
const port = process.env.PORT || 3000;

// Whitelist of allowed client origins
const allowedOrigins = [
    'http://localhost:3000',
    'http://your-production-domain.com'
];

// Strict CORS configuration for protected routes
const strictCorsOptions = {
    origin: (origin: string | undefined, callback: (err: Error | null, allow?: boolean) => void) => {
        if (!origin || allowedOrigins.includes(origin)) {
            callback(null, true);
        } else {
            callback(new Error('Not allowed by CORS'));
        }
    },
    methods: ['GET', 'POST'],
    credentials: true
};

// Open CORS configuration for public routes
const openCorsOptions = {
    origin: '*',
    methods: ['GET', 'POST'],
    credentials: true
};

// Middleware
app.use(express.json());

// Public route example (no CORS restrictions)
app.get('/api/public', cors(openCorsOptions), (req, res) => {
    res.json({ message: 'This is a public endpoint' });
});

// Protected route with strict CORS and authentication
app.post('/api/addKey', 
    cors(strictCorsOptions),
    (req, res) => {
        res.json({ message: 'Access granted to protected route' });
    }
);

app.listen(port, () => {
    console.log(`Server running on port ${port}`);
});