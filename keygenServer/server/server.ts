import express, { Request, Response } from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import prisma from './prisma_client';
import crypto from 'crypto';


dotenv.config();

const app = express();
const port = process.env.PORT || 3001;

// Whitelist of allowed client origins
const allowedOrigins = [
    'http://localhost:3000',
    'https://mcp-hackathon.vercel.app/',
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

app.use(cors({
    origin: allowedOrigins,
    credentials: true,
    methods: ['GET', 'POST', 'OPTIONS']
}));

// Middleware
app.use(express.json());


function generateApiKey(): string {
    return crypto.randomBytes(32).toString('hex');
}

// Public route example (no CORS restrictions)
app.post('/api/verifyKey',
    cors(openCorsOptions),
    async (req: Request, res: Response) => {
        try {
            const { apiKey } = req.body;

            if (!apiKey) {
                res.status(400).json({ error: 'API key is required' });
                return;
            }

            const key = await prisma.key.findFirst({
                where: {
                    apiKey
                }
            });

            if (!key) {
                res.status(401).json({ valid: false });
                return;
            }
            else {
                res.json({ valid: true });
            }

        } catch (error) {
            console.error('Error verifying API key:', error);
            res.status(500).json({ error: 'Failed to verify API key' });
        }
    }
);

// Protected route with strict CORS and authentication
app.post('/api/addKey', 
    cors(strictCorsOptions),
    async (req: Request, res: Response): Promise<void> => {
        try {
            const { email } = req.body;

            if (!email) {
                res.status(400).json({ error: 'Email is required' });
                return;
            }

            const apiKey = generateApiKey();
            
            const newKey = await prisma.key.create({
                data: {
                    email,
                    apiKey,
                }
            });

            res.json({ 
                message: 'API key generated successfully',
                apiKey: newKey.apiKey 
            });
        } catch (error) {
            console.error('Error creating API key:', error);
            res.status(500).json({ error: 'Failed to create API key' });
        }
    }
);

app.listen(port, () => {
    console.log(`Server running on port ${port}`);
});