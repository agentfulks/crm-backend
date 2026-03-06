import { getCard } from '@/lib/trello';
import { NextRequest, NextResponse } from 'next/server';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ cardId: string }> }
) {
  try {
    const { cardId } = await params;
    const card = await getCard(cardId);
    return NextResponse.json(card);
  } catch (error) {
    console.error('Error fetching card:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to fetch card' },
      { status: 500 }
    );
  }
}