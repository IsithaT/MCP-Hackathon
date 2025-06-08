'use client';
import { useEffect, useState } from 'react';
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
  }, [router]);

  const handleSignOut = async () => {
    const { auth } = await import('@/libs/firebase');
    await auth.signOut();
    router.push('/');
  };

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

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(apiKey);
      const toast = document.createElement('div');
      toast.textContent = 'API key copied to clipboard!';
      toast.className = 'fixed top-4 right-4 neuro-card px-4 py-2 text-sm text-primary font-medium z-50 transition-opacity duration-300';
      document.body.appendChild(toast);
      setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => document.body.removeChild(toast), 300);
      }, 2000);
    } catch (err) {
      console.error('Failed to copy to clipboard:', err);
    }
  }; if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="neuro-container p-6">
          <div className="flex items-center space-x-3">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
            <span className="text-base text-secondary">Loading...</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-4 md:p-6 flex justify-center items-center">
      <div className="w-full max-w-4xl py-6 ">
        {/* Header */}
        <div className="neuro-container p-4 md:p-6 mb-6">
          <div className="flex justify-between items-center gap-4">
            <div>
              <h1 className="text-xl md:text-2xl font-bold text-primary mb-1">
                Welcome back, {userDisplayName}!
              </h1>
              <p className="text-sm md:text-base text-secondary">
                Generate your MCP API key for monitoring APIs
              </p>
            </div>
            <button
              onClick={handleSignOut}
              className="neuro-button px-3 py-2 md:px-4 md:py-2 text-sm md:text-base text-button font-medium"
            >
              Sign Out
            </button>
          </div>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-6">          {/* API Key Generation */}
          <div className="neuro-card p-4 md:p-6">
            <h2 className="text-lg md:text-xl font-semibold text-primary mb-4">
              Generate MCP API Key
            </h2>

            <div className="space-y-4">
              <button
                onClick={generateApiKey}
                className="neuro-button-primary w-full py-3 px-4 text-base md:text-lg font-semibold"
              >
                <span className="flex items-center justify-center space-x-2">
                  <span>Generate New MCP API Key</span>
                </span>
              </button>              {apiKey && (
                <div className="neuro-display p-4">
                  <div className="flex justify-between items-center mb-3">
                    <h3 className="text-sm md:text-base font-semibold text-primary">Your MCP API Key</h3>
                    <button
                      onClick={copyToClipboard}
                      className="neuro-button px-2 py-1 text-xs text-button"
                      title="Copy to clipboard"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                      </svg>
                    </button>
                  </div>
                  <div className="neuro-input p-3">
                    <code className="text-sm text-primary font-mono break-all">
                      {apiKey}
                    </code>
                  </div>
                  <p className="text-xs text-secondary mt-2">
                    Keep this key secure
                  </p>
                </div>
              )}              {error && (
                <div className="neuro-display p-3 border-l-4 border-red-400">
                  <div className="flex items-center">
                    <svg className="w-4 h-4 text-red-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span className="text-red-700 text-sm font-medium">{error}</span>
                  </div>
                </div>
              )}
            </div>
          </div>          {/* User Info & Instructions */}
          <div className="space-y-4">
            {/* User Profile */}
            <div className="neuro-card p-4 md:p-6">
              <h2 className="text-lg md:text-xl font-semibold text-primary mb-4">
                Account Information
              </h2>
              <div className="space-y-3">
                <div className="neuro-display p-3 flex flex-col space-y-4">
                  <div>
                    <label className="text-xs font-medium text-secondary">Email</label>
                    <p className="text-primary font-medium">{userEmail}</p>
                  </div>

                  <div>
                    <label className="text-xs font-medium text-secondary">Display Name</label>
                    <p className="text-primary font-medium">{userDisplayName}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Usage Instructions */}
            <div className="neuro-card p-4 md:p-6">
              <h2 className="text-lg md:text-xl font-semibold text-primary mb-4">
                How to Use Your MCP API Key
              </h2>
              <div className="space-y-3 text-sm text-secondary">
                <div className="flex items-start space-x-3">
                  <span className="flex-shrink-0 w-5 h-5 bg-slate-600 text-white rounded-full flex items-center justify-center text-xs font-semibold">1</span>
                  <p>Use this key with the MCP API monitoring system to track APIs</p>
                </div>
                <div className="flex items-start space-x-3">
                  <span className="flex-shrink-0 w-5 h-5 bg-slate-600 text-white rounded-full flex items-center justify-center text-xs font-semibold">2</span>
                  <p>Set up API monitoring rules for automated API calls</p>
                </div>
                <div className="flex items-start space-x-3">
                  <span className="flex-shrink-0 w-5 h-5 bg-slate-600 text-white rounded-full flex items-center justify-center text-xs font-semibold">3</span>
                  <p>Monitor API responses and receive alerts when services change</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}