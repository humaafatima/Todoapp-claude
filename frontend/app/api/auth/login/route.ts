import { NextRequest, NextResponse } from 'next/server';
import jwt from 'jsonwebtoken';

const JWT_SECRET = process.env.NEXT_PUBLIC_JWT_SECRET || 'your-super-secret-key-change-in-production-12345678';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { username } = body;

    if (!username || !username.trim()) {
      return NextResponse.json(
        { error: 'Username is required' },
        { status: 400 }
      );
    }

    // Generate JWT token (in a real app, validate credentials first)
    const token = jwt.sign(
      { sub: username.trim() },
      JWT_SECRET,
      {
        algorithm: 'HS256',
        expiresIn: '24h'
      }
    );

    return NextResponse.json({
      token,
      userId: username.trim()
    });
  } catch (error) {
    console.error('Login error:', error);
    return NextResponse.json(
      { error: 'Login failed' },
      { status: 500 }
    );
  }
}
