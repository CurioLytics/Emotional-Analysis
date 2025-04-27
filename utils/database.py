"""
Database utility functions.

This module provides functions for interacting with the Supabase database,
including connection management and common database operations.
"""

import os
import logging
import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
from typing import Optional, Dict, Any, List

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def get_supabase_client() -> Client:
    """
    Initialize and return a Supabase client with credentials from environment variables.
    
    Returns:
        Client: Initialized Supabase client
        
    Raises:
        ValueError: If Supabase credentials are missing or invalid
    """
    # Explicitly load environment variables again to ensure they're available
    load_dotenv()
    
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        error_msg = "Supabase credentials not found in environment variables"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    try:
        client = create_client(url, key)
        # Test the connection with a simple query
        test_response = client.table("documents").select("id").limit(1).execute()
        logger.info("Supabase connection successful")
        return client
    except Exception as e:
        error_msg = f"Failed to connect to Supabase: {str(e)}"
        logger.error(error_msg)
        raise ConnectionError(error_msg)

def execute_query(
    table: str, 
    query_type: str = "select", 
    columns: str = "*", 
    filters: Optional[Dict[str, Any]] = None,
    order_by: Optional[Dict[str, str]] = None,
    limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Execute a query on the Supabase database.
    
    Args:
        table: Name of the table to query
        query_type: Type of query (select, insert, update, delete)
        columns: Columns to select (for select queries)
        filters: Dictionary of filters to apply (column: value)
        order_by: Dictionary of order by clauses (column: direction)
        limit: Maximum number of records to return
        
    Returns:
        List of records matching the query
        
    Raises:
        ValueError: If invalid query parameters are provided
        ConnectionError: If database connection fails
    """
    client = get_supabase_client()
    
    try:
        query = client.table(table)
        
        if query_type == "select":
            query = query.select(columns)
        elif query_type not in ["insert", "update", "delete"]:
            raise ValueError(f"Invalid query type: {query_type}")
        
        # Apply filters
        if filters:
            for column, value in filters.items():
                query = query.eq(column, value)
        
        # Apply order by
        if order_by and query_type == "select":
            for column, direction in order_by.items():
                query = query.order(column, desc=(direction.lower() == "desc"))
        
        # Apply limit
        if limit and query_type == "select":
            query = query.limit(limit)
        
        # Execute query
        response = query.execute()
        
        return response.data
    except Exception as e:
        error_msg = f"Database query error: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)
