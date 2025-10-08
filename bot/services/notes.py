"""Notes and file management service with Notion and Google Drive integration."""

import logging
import asyncio
import os
import tempfile
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import mimetypes

import httpx
from notion_client import AsyncClient as NotionClient
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io

from bot.config import settings
from bot.services.n8n import n8n_service
from bot.utils.metrics import request_counter


logger = logging.getLogger(__name__)


class NotesService:
    """Service for notes and file management."""
    
    def __init__(self):
        # Notion setup
        self.notion = None
        if settings.notion_token:
            self.notion = NotionClient(auth=settings.notion_token)
        
        # Google Drive setup
        self.drive_service = None
        if settings.google_drive_credentials:
            try:
                creds = Credentials.from_authorized_user_info(
                    json.loads(settings.google_drive_credentials)
                )
                self.drive_service = build('drive', 'v3', credentials=creds)
            except Exception as e:
                logger.error(f"Error setting up Google Drive: {e}")
        
        # Local notes storage
        self.notes_dir = "data/notes"
        os.makedirs(self.notes_dir, exist_ok=True)
    
    async def create_notion_page(
        self,
        title: str,
        content: str,
        database_id: Optional[str] = None,
        tags: List[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Create a new page in Notion."""
        if not self.notion:
            return None
        
        try:
            request_counter.inc()
            
            # Prepare page properties
            properties = {
                "Name": {
                    "title": [
                        {
                            "text": {
                                "content": title
                            }
                        }
                    ]
                }
            }
            
            # Add tags if provided
            if tags:
                properties["Tags"] = {
                    "multi_select": [
                        {"name": tag} for tag in tags
                    ]
                }
            
            # Prepare content blocks
            children = []
            
            # Split content into paragraphs
            paragraphs = content.split('\n\n')
            for paragraph in paragraphs:
                if paragraph.strip():
                    children.append({
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": paragraph.strip()
                                    }
                                }
                            ]
                        }
                    })
            
            # Create page
            if database_id:
                # Create in database
                page = await self.notion.pages.create(
                    parent={"database_id": database_id},
                    properties=properties,
                    children=children
                )
            else:
                # Create as standalone page
                page = await self.notion.pages.create(
                    parent={"type": "page_id", "page_id": settings.notion_parent_page_id or ""},
                    properties=properties,
                    children=children
                )
            
            return {
                "id": page["id"],
                "url": page["url"],
                "title": title,
                "created_time": page["created_time"]
            }
            
        except Exception as e:
            logger.error(f"Error creating Notion page: {e}")
            return None
    
    async def search_notion_pages(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search Notion pages."""
        if not self.notion:
            return []
        
        try:
            request_counter.inc()
            
            results = await self.notion.search(
                query=query,
                page_size=max_results,
                filter={
                    "property": "object",
                    "value": "page"
                }
            )
            
            pages = []
            for page in results.get("results", []):
                title = "Untitled"
                if page.get("properties", {}).get("Name", {}).get("title"):
                    title = page["properties"]["Name"]["title"][0]["text"]["content"]
                elif page.get("properties", {}).get("title", {}).get("title"):
                    title = page["properties"]["title"]["title"][0]["text"]["content"]
                
                pages.append({
                    "id": page["id"],
                    "title": title,
                    "url": page["url"],
                    "created_time": page["created_time"],
                    "last_edited_time": page["last_edited_time"]
                })
            
            return pages
            
        except Exception as e:
            logger.error(f"Error searching Notion pages: {e}")
            return []
    
    async def get_notion_databases(self) -> List[Dict[str, Any]]:
        """Get available Notion databases."""
        if not self.notion:
            return []
        
        try:
            results = await self.notion.search(
                filter={
                    "property": "object",
                    "value": "database"
                }
            )
            
            databases = []
            for db in results.get("results", []):
                title = "Untitled Database"
                if db.get("title"):
                    title = db["title"][0]["text"]["content"]
                
                databases.append({
                    "id": db["id"],
                    "title": title,
                    "url": db["url"],
                    "created_time": db["created_time"]
                })
            
            return databases
            
        except Exception as e:
            logger.error(f"Error getting Notion databases: {e}")
            return []
    
    async def upload_to_google_drive(
        self,
        file_path: str,
        filename: str,
        folder_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Upload file to Google Drive."""
        if not self.drive_service:
            return None
        
        try:
            request_counter.inc()
            
            # Determine MIME type
            mime_type, _ = mimetypes.guess_type(filename)
            if not mime_type:
                mime_type = 'application/octet-stream'
            
            # Prepare file metadata
            file_metadata = {
                'name': filename,
                'description': f'Uploaded via Telegram Bot on {datetime.now().isoformat()}'
            }
            
            if folder_id:
                file_metadata['parents'] = [folder_id]
            
            # Upload file
            media = MediaFileUpload(file_path, mimetype=mime_type)
            
            # Run in thread pool since Google API is synchronous
            loop = asyncio.get_event_loop()
            file = await loop.run_in_executor(
                None,
                lambda: self.drive_service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id,name,webViewLink,size,mimeType,createdTime'
                ).execute()
            )
            
            return {
                "id": file["id"],
                "name": file["name"],
                "url": file["webViewLink"],
                "size": int(file.get("size", 0)),
                "mime_type": file["mimeType"],
                "created_time": file["createdTime"]
            }
            
        except Exception as e:
            logger.error(f"Error uploading to Google Drive: {e}")
            return None
    
    async def search_google_drive(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search Google Drive files."""
        if not self.drive_service:
            return []
        
        try:
            request_counter.inc()
            
            # Build search query
            search_query = f"name contains '{query}' and trashed=false"
            
            # Run in thread pool
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None,
                lambda: self.drive_service.files().list(
                    q=search_query,
                    pageSize=max_results,
                    fields="files(id,name,webViewLink,size,mimeType,createdTime,modifiedTime)"
                ).execute()
            )
            
            files = []
            for file in results.get("files", []):
                files.append({
                    "id": file["id"],
                    "name": file["name"],
                    "url": file["webViewLink"],
                    "size": int(file.get("size", 0)),
                    "mime_type": file["mimeType"],
                    "created_time": file["createdTime"],
                    "modified_time": file["modifiedTime"]
                })
            
            return files
            
        except Exception as e:
            logger.error(f"Error searching Google Drive: {e}")
            return []
    
    async def download_from_google_drive(self, file_id: str, output_path: str) -> bool:
        """Download file from Google Drive."""
        if not self.drive_service:
            return False
        
        try:
            request_counter.inc()
            
            # Run in thread pool
            loop = asyncio.get_event_loop()
            
            def download_file():
                request = self.drive_service.files().get_media(fileId=file_id)
                fh = io.BytesIO()
                downloader = MediaIoBaseDownload(fh, request)
                
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                
                # Write to file
                with open(output_path, 'wb') as f:
                    f.write(fh.getvalue())
                
                return True
            
            result = await loop.run_in_executor(None, download_file)
            return result
            
        except Exception as e:
            logger.error(f"Error downloading from Google Drive: {e}")
            return False
    
    async def create_local_note(
        self,
        user_id: int,
        title: str,
        content: str,
        tags: List[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Create a local note file."""
        try:
            # Create user directory
            user_dir = os.path.join(self.notes_dir, str(user_id))
            os.makedirs(user_dir, exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{timestamp}_{safe_title[:50]}.md"
            file_path = os.path.join(user_dir, filename)
            
            # Create note content
            note_content = f"# {title}\n\n"
            note_content += f"**Created:** {datetime.now().isoformat()}\n"
            if tags:
                note_content += f"**Tags:** {', '.join(tags)}\n"
            note_content += "\n---\n\n"
            note_content += content
            
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(note_content)
            
            # Log to n8n
            await n8n_service.trigger_n8n_workflow("note_created", {
                "user_id": user_id,
                "title": title,
                "file_path": file_path,
                "tags": tags or [],
                "created_at": datetime.now().isoformat()
            })
            
            return {
                "title": title,
                "file_path": file_path,
                "filename": filename,
                "size": os.path.getsize(file_path),
                "created_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error creating local note: {e}")
            return None
    
    async def search_local_notes(self, user_id: int, query: str) -> List[Dict[str, Any]]:
        """Search local notes for a user."""
        try:
            user_dir = os.path.join(self.notes_dir, str(user_id))
            if not os.path.exists(user_dir):
                return []
            
            notes = []
            query_lower = query.lower()
            
            for filename in os.listdir(user_dir):
                if filename.endswith('.md'):
                    file_path = os.path.join(user_dir, filename)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Check if query matches filename or content
                        if query_lower in filename.lower() or query_lower in content.lower():
                            # Extract title from content
                            lines = content.split('\n')
                            title = lines[0].replace('# ', '') if lines else filename
                            
                            notes.append({
                                "title": title,
                                "filename": filename,
                                "file_path": file_path,
                                "size": os.path.getsize(file_path),
                                "modified_time": datetime.fromtimestamp(
                                    os.path.getmtime(file_path)
                                ).isoformat(),
                                "preview": content[:200] + "..." if len(content) > 200 else content
                            })
                    except Exception as e:
                        logger.error(f"Error reading note file {filename}: {e}")
            
            # Sort by modification time (newest first)
            notes.sort(key=lambda x: x["modified_time"], reverse=True)
            return notes
            
        except Exception as e:
            logger.error(f"Error searching local notes: {e}")
            return []
    
    async def get_user_notes(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent notes for a user."""
        try:
            user_dir = os.path.join(self.notes_dir, str(user_id))
            if not os.path.exists(user_dir):
                return []
            
            notes = []
            
            for filename in os.listdir(user_dir):
                if filename.endswith('.md'):
                    file_path = os.path.join(user_dir, filename)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Extract title
                        lines = content.split('\n')
                        title = lines[0].replace('# ', '') if lines else filename
                        
                        notes.append({
                            "title": title,
                            "filename": filename,
                            "file_path": file_path,
                            "size": os.path.getsize(file_path),
                            "modified_time": datetime.fromtimestamp(
                                os.path.getmtime(file_path)
                            ).isoformat(),
                            "preview": content[:150] + "..." if len(content) > 150 else content
                        })
                    except Exception as e:
                        logger.error(f"Error reading note file {filename}: {e}")
            
            # Sort by modification time and limit
            notes.sort(key=lambda x: x["modified_time"], reverse=True)
            return notes[:limit]
            
        except Exception as e:
            logger.error(f"Error getting user notes: {e}")
            return []


# Global notes service instance
notes_service = NotesService()
