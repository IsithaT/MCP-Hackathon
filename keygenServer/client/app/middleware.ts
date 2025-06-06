// middleware.ts
import { NextRequest, NextResponse } from 'next/server';

export function middleware(req: NextRequest) {
  const isAuth = req.cookies.get('auth')?.value;
  if (!isAuth && req.nextUrl.pathname.startsWith('/main')) {
    return NextResponse.redirect(new URL('/', req.url));
  }
}
