#!/usr/bin/env python3
"""
OpenClaw Context Manager - Integration Script
Demonstrates hook points for pre-compaction chunking
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add skills directory to path
sys.path.insert(0, str(Path(__file__).parent))

from chunking_service import get_chunker, ContextMetadata, PriorityLevel, ContextType


class ContextCompactionHook:
    """
    Hook interface for OpenClaw compaction events.
    
    This class demonstrates how to integrate chonkie-based chunking
    into OpenClaw's compaction workflow.
    """
    
    def __init__(self, workspace_path: str = "~/.openclaw/workspace"):
        self.chunker = get_chunker(workspace_path)
        
    async def on_pre_compaction(self, 
                                session_id: str,
                                context_text: str,
                                current_tokens: int,
                                max_tokens: int) -> Dict[str, Any]:
        """
        Called before OpenClaw compacts session context.
        
        Args:
            session_id: Unique session identifier
            context_text: Full context that will be compacted
            current_tokens: Current token count
            max_tokens: Model's maximum context window
            
        Returns:
            Dictionary with chunked context and metadata
        """
        print(f"[ContextHook] Pre-compaction for session {session_id[:8]}")
        print(f"[ContextHook] Tokens: {current_tokens}/{max_tokens}")
        
        # Determine target tier based on token pressure
        token_pressure = current_tokens / max_tokens
        if token_pressure > 0.9:
            target_tier = "cold"
        elif token_pressure > 0.7:
            target_tier = "warm"
        else:
            target_tier = "warm"  # Default
        
        # Create metadata for chunks
        metadata = ContextMetadata(
            chunk_id="demo-chunk",
            session_id=session_id,
            priority=PriorityLevel.HIGH,
            context_type=ContextType.COMPACTION_SUMMARY,
            current_tier=target_tier,
            token_count=current_tokens
        )
        
        # Chunk the context
        chunks = self.chunker.chunk_text(
            text=context_text,
            tier=target_tier,
            metadata=metadata
        )
        
        # Store in appropriate tier
        self.chunker.store_chunks(chunks)
        
        # Return compaction summary
        return {
            "session_id": session_id,
            "target_tier": target_tier,
            "chunks_created": len(chunks),
            "total_tokens": sum(c["token_count"] for c in chunks),
            "action": "chunked_and_stored"
        }
    
    async def on_memory_flush(self,
                             session_id: str,
                             memory_content: str) -> Dict[str, Any]:
        """
        Called during memory flush (pre-compaction ping).
        
        Args:
            session_id: Session being flushed
            memory_content: Content to be written to memory files
            
        Returns:
            Dictionary with chunked memory references
        """
        print(f"[ContextHook] Memory flush for session {session_id[:8]}")
        
        # Memory gets warm-tier treatment
        metadata = ContextMetadata(
            chunk_id="demo-chunk",
            session_id=session_id,
            priority=PriorityLevel.NORMAL,
            context_type=ContextType.MEMORY_REF,
            current_tier="warm"
        )
        
        chunks = self.chunker.chunk_text(
            text=memory_content,
            tier="warm",
            metadata=metadata
        )
        
        self.chunker.store_chunks(chunks)
        
        return {
            "session_id": session_id,
            "memory_chunks": len(chunks),
            "indexed": True
        }
    
    async def retrieve_relevant_context(self,
                                       session_id: str,
                                       query: str,
                                       limit: int = 5) -> Dict[str, Any]:
        """
        Retrieve relevant context chunks for a query.
        
        Args:
            session_id: Session to search within
            query: Search query
            limit: Maximum results
            
        Returns:
            Dictionary with retrieved chunks
        """
        print(f"[ContextHook] Retrieving context for query: {query[:50]}...")
        
        # Retrieve from warm tier
        chunks = self.chunker.retrieve_chunks(
            session_id=session_id,
            tier="warm",
            limit=limit
        )
        
        return {
            "session_id": session_id,
            "query": query,
            "results": chunks,
            "result_count": len(chunks)
        }


async def demo():
    """Demonstrate context manager integration."""
    print("=" * 70)
    print("OpenClaw Context Manager - Integration Demo")
    print("=" * 70)
    
    hook = ContextCompactionHook()
    
    # Simulate a large context that needs compaction
    sample_context = """
    # Project Discussion Session
    
    ## Initial Requirements
    User wants to build a context management system for OpenClaw using chonkie.
    Requirements:
    1. Three-tier architecture (hot/warm/cold)
    2. Semantic chunking for better retrieval
    3. Optimized for 32GB RAM environments
    
    ## Technical Decisions
    - Use RecursiveChunker for hot tier (speed)
    - Use SemanticChunker for warm/cold (quality)
    - all-MiniLM-L6-v2 for embeddings (efficiency)
    - sqlite-vec for vector storage (zero-config)
    
    ## Implementation Notes
    The chunking service should integrate with OpenClaw's compaction hooks.
    Pre-compaction: Chunk and store context
    Memory flush: Index memory references
    Retrieval: Search vector DB for relevant context
    
    """ * 10  # Multiply to simulate large context
    
    session_id = "demo-session-123"
    current_tokens = 15000
    max_tokens = 32000
    
    # Simulate pre-compaction hook
    result = await hook.on_pre_compaction(
        session_id=session_id,
        context_text=sample_context,
        current_tokens=current_tokens,
        max_tokens=max_tokens
    )
    
    print("\n--- Compaction Result ---")
    print(json.dumps(result, indent=2))
    
    # Simulate memory flush
    memory_content = "Remember: Context manager uses 512/1024/2048 token chunks for hot/warm/cold tiers."
    
    flush_result = await hook.on_memory_flush(
        session_id=session_id,
        memory_content=memory_content
    )
    
    print("\n--- Memory Flush Result ---")
    print(json.dumps(flush_result, indent=2))
    
    # Simulate context retrieval
    query = "What chunk sizes should I use?"
    
    retrieve_result = await hook.retrieve_relevant_context(
        session_id=session_id,
        query=query,
        limit=3
    )
    
    print("\n--- Retrieval Result ---")
    print(json.dumps(retrieve_result, indent=2, default=str))
    
    print("\n" + "=" * 70)
    print("Demo complete!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(demo())