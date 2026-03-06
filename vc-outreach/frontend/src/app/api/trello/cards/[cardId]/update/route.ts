import { updateCard } from '@/lib/trello';
import { NextRequest, NextResponse } from 'next/server';

export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ cardId: string }> }
) {
  try {
    const { cardId } = await params;
    const body = await request.json();
    await updateCard(cardId, {
      draftMessage: body.draftMessage,
      notes: body.notes,
    });
    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Error updating card:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to update card' },
      { status: 500 }
    );
  }
}