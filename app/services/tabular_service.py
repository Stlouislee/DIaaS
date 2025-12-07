from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List, Dict, Any, Optional

class TabularService:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _get_table_name(self, dataset_id: str) -> str:
        # Sanitize just in case, though UUID is safe
        return f"dataset_{dataset_id.replace('-', '_')}"

    async def create_table(self, dataset_id: str, schema: Dict[str, str]):
        """
        Creates a physical table for the dataset.
        Schema maps column_name -> sql_type (e.g., "age": "INTEGER")
        """
        table_name = self._get_table_name(dataset_id)
        columns_def = ", ".join([f'"{col}" {dtype}' for col, dtype in schema.items()])
        
        # Add a primary key ID for rows
        sql = f'CREATE TABLE "{table_name}" (id SERIAL PRIMARY KEY, {columns_def});'
        
        await self.db.execute(text(sql))
        await self.db.commit()

    async def insert_rows(self, dataset_id: str, rows: List[Dict[str, Any]]):
        if not rows:
            return
            
        table_name = self._get_table_name(dataset_id)
        columns = rows[0].keys()
        col_names = ", ".join([f'"{c}"' for c in columns])
        placeholders = ", ".join([f':{c}' for c in columns])
        
        sql = f'INSERT INTO "{table_name}" ({col_names}) VALUES ({placeholders})'
        
        await self.db.execute(text(sql), rows)
        await self.db.commit()

    async def query_rows(
        self, 
        dataset_id: str, 
        limit: int = 100, 
        offset: int = 0,
        filters: Optional[Dict[str, str]] = None,
        sort: Optional[str] = None,
        select_cols: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        table_name = self._get_table_name(dataset_id)
        
        # Selection
        params = {"limit": limit, "offset": offset}
        sel_clause = "*"
        if select_cols:
            sel_clause = ", ".join([f'"{c}"' for c in select_cols])
            
        sql = f'SELECT {sel_clause} FROM "{table_name}"'
        
        # Filtering (Simple AND logic for now)
        where_clauses = []
        if filters:
            for i, (col, val) in enumerate(filters.items()):
                # Parse op e.g. "age=gt:30" handled at caller, here we expect "col": "val" or special handling
                # For safety, we'll assume caller parsed it or we use simplistic "col = :val" for now
                # To support rich query "gt:", "lt:", we need a parser.
                # IMPLEMENTING BASIC EQUALITY FOR V1
                param_name = f"filter_{i}"
                where_clauses.append(f'"{col}" = :{param_name}')
                params[param_name] = val
        
        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)

        # Sorting
        if sort:
            # Expected format "col:desc" or "col"
            parts = sort.split(':')
            col = parts[0]
            direction = parts[1] if len(parts) > 1 else 'asc'
            if direction.lower() not in ['asc', 'desc']:
                direction = 'asc'
            sql += f' ORDER BY "{col}" {direction}'

        sql += " LIMIT :limit OFFSET :offset"
        
        result = await self.db.execute(text(sql), params)
        return [dict(row._mapping) for row in result]

    async def drop_table(self, dataset_id: str):
        table_name = self._get_table_name(dataset_id)
        await self.db.execute(text(f'DROP TABLE IF EXISTS "{table_name}"'))
        await self.db.commit()
