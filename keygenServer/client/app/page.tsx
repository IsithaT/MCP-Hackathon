'use client';
import { auth, googleProvider } from '@/lib/firebase';
import { signInWithPopup } from 'firebase/auth';
import { useRouter } from 'next/navigation';

export default function LoginPage() {
  const router = useRouter();

  const signInWithGoogle = async () => {
    try {
      await signInWithPopup(auth, googleProvider);
      router.push('/main');
    } catch (err) {
      alert('Login failed');
      console.error(err);
    }
  };

  return (
    <main className="p-4">
      <h1 className="text-xl mb-4">Sign In</h1>
      <button onClick={signInWithGoogle} className="bg-blue-500 text-white px-4 py-2 rounded">
        Sign in with Google
      </button>
    </main>
  );
}

