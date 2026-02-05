import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const token = request.cookies.get('auth_token')?.value;
  const isLoginPage = request.nextUrl.pathname === '/login';
  const isDashboard = request.nextUrl.pathname.startsWith('/dashboard');

  // If accessing dashboard without token, redirect to login
  if (isDashboard && !token) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  // If accessing login with token, redirect to dashboard
  if (isLoginPage && token) {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/dashboard/:path*', '/login'],
};
