import express, { Request, Response } from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { prisma } from './prisma_client';
import crypto from 'crypto';


dotenv.config();

const app = express();
const port = process.env.PORT || 3001;

// Whitelist of allowed client origins
const allowedOrigins = [
    // for testing
    'http://localhost:3000',
    // deployed frontend
    'https://mcp-hackathon.vercel.app'
];

// Strict CORS configuration for protected routes
const strictCorsOptions = {
    origin: (origin: string | undefined, callback: (err: Error | null, allow?: boolean) => void) => {
        // disallows CURL, Postman, etc.
        if (origin && allowedOrigins.includes(origin)) {
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
    methods: ['GET', 'POST', 'OPTIONS'],
    credentials: true
};


// Middleware
app.use(express.json());

// Generates Key
// TODO: add verification that key doesn't exist and add key if needed.
//          currently relying on sheer probablistic chance :P
function generateApiKey(): string {
    return crypto.randomBytes(32).toString('hex');
}

// Public route (no CORS restrictions)
app.post('/api/verifyKey',
    cors(openCorsOptions),
    async (req: Request, res: Response) => {
        try {
            const { apiKey } = req.body;

            if (!apiKey) {
                res.status(400).json({ error: 'API key is required' });
                return;
            }

            // See if key is in database
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
app.options('/api/addKey', cors(strictCorsOptions));
app.options('/api/addKey/', cors(strictCorsOptions));
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
            
            // Add key to database
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
