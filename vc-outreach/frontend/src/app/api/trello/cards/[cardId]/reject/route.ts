import { rejectCard } from '@/lib/trello';
import { NextRequest, NextResponse } from 'next/server';

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ cardId: string }> }
) {
  try {
    const { cardId } = await params;
    const body = await request.json();
    await rejectCard(cardId, body.reason);
    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Error rejecting card:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to reject card' },
      { status: 500 }
    );
  }
}