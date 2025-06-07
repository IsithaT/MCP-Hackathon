'use client';
import { useEffect, useState } from 'react';
import { auth } from '@/libs/firebase';
import { useRouter } from 'next/navigation';

export default function MainPage() {
  const [loading, setLoading] = useState(true);
  const [userEmail, setUserEmail] = useState('');
  const [userDisplayName, setUserDisplayName] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [error, setError] = useState('');
  const router = useRouter();

  useEffect(() => {
    const unsub = auth.onAuthStateChanged((user) => {
      if (!user) {
        router.push('/');
      } else {
        setUserEmail(user.email || 'Unknown user');
        setUserDisplayName(user.displayName || 'Unknown user');
        setLoading(false);
      }
    });
    return () => unsub();
  }, []);

  const generateApiKey = async () => {
    try {
      const response = await fetch('http://localhost:3001/api/addKey', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email: userEmail }),
      });

      if (!response.ok) {
        throw new Error('Failed to generate API key');
      }

      const data = await response.json();
      setApiKey(data.apiKey);
      setError('');
    } catch (err) {
      setError('Failed to generate API key');
      console.error('Error:', err);
    }
  };

  if (loading) return <p>Loading...</p>;

  return (
    <main className="p-4">
      <h1 className="text-xl mb-4">Welcome, {userDisplayName}!</h1>
      
      <div className="space-y-4">
        <button 
          onClick={generateApiKey}
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
        >
          Generate API Key
        </button>

        {apiKey && (
          <div className="mt-4 p-4 bg-gray-100 rounded">
            <p className="font-semibold">Your API Key:</p>
            <code className="block mt-2 p-2 bg-white rounded border">{apiKey}</code>
          </div>
        )}

        {error && (
          <div className="mt-4 p-4 bg-red-100 text-red-700 rounded">
            {error}
          </div>
        )}

        <button 
          onClick={() => auth.signOut().then(() => router.push('/'))}
          className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded"
        >
          Logout
        </button>
      </div>
    </main>
  );
}