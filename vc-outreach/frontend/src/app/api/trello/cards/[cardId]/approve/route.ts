import { approveCard } from '@/lib/trello';
import { NextRequest, NextResponse } from 'next/server';

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ cardId: string }> }
) {
  try {
    const { cardId } = await params;
    await approveCard(cardId);
    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Error approving card:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to approve card' },
      { status: 500 }
    );
  }
}