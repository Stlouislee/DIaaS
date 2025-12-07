from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Dict, Any, Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.core.neo4j_db import get_neo4j_driver
from app.core.security import get_current_user_id
from app.models.session import Session

router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    type: str # "sql" or "cypher"
    params: Dict[str, Any] = {}

@router.post("/{session_id}/query")
async def execute_query(
    session_id: str,
    request: QueryRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    driver = Depends(get_neo4j_driver)
):
    # Verify Session
    sess = await db.get(Session, session_id)
    if not sess or sess.user_id != user_id:
        raise HTTPException(status_code=404, detail="Session not found")

    if request.type.lower() == "sql":
        try:
            # Execute raw SQL
            # Security Note: This allows full access to the Postgres DB as the app user.
            # In a real PROD env, we'd restrict this user permissions or parse the SQL to whitelist tables.
            # For this task, we assume "Power User" access as requested.
            result = await db.execute(text(request.query), request.params)
            
            # Helper to serialize rows
            if result.returns_rows:
                rows = [dict(row._mapping) for row in result]
                return {"status": "success", "data": rows, "count": len(rows)}
            else:
                await db.commit()
                return {"status": "success", "rowcount": result.rowcount}
                
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=400, detail=f"SQL Error: {str(e)}")

    elif request.type.lower() == "cypher":
        try:
            async with driver.session() as session:
                result = await session.run(request.query, request.params)
                # Serialize generic Cypher result is complex (Nodes, Relationships, Paths, primitive types)
                # We do a best-effort simple recursive serializer
                data = []
                async for record in result:
                    data.append(record.data())
                return {"status": "success", "data": data, "count": len(data)}
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Cypher Error: {str(e)}")

    else:
         raise HTTPException(status_code=400, detail="Invalid query type. Must be 'sql' or 'cypher'.")
