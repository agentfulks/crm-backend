import { getApprovalCards } from '@/lib/trello';
import { NextResponse } from 'next/server';

export async function GET() {
  try {
    const cards = await getApprovalCards();
    return NextResponse.json(cards);
  } catch (error) {
    console.error('Error fetching cards:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to fetch cards' },
      { status: 500 }
    );
  }
}