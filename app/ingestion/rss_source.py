import feedparser
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from app.ingestion.base import BaseExtractor
from app.schemas.data import UnifiedDataCreate
import time

class RSSExtractor(BaseExtractor):
    def __init__(self, db, feed_url: str, run_id: Optional[str] = None):
        super().__init__(source_name="rss_news", db=db, run_id=run_id)
        self.feed_url = feed_url

    def extract(self, last_checkpoint: Optional[datetime]) -> List[Dict[str, Any]]:
        feed = feedparser.parse(self.feed_url)
        entries = []
        
        for entry in feed.entries:
            # Convert published_parsed to datetime (aware)
            published = None
            if hasattr(entry, 'published_parsed'):
                published = datetime.fromtimestamp(time.mktime(entry.published_parsed), tz=timezone.utc)
            
            if not last_checkpoint or (published and published > last_checkpoint):
                entries.append({
                    'id': entry.get('id', entry.link),
                    'title': entry.title,
                    'summary': entry.get('summary', ''),
                    'link': entry.link,
                    'published': published.isoformat() if published else None
                })
        
        return entries

    def transform(self, raw_data: Dict[str, Any]) -> UnifiedDataCreate:
        return UnifiedDataCreate(
            source=self.source_name,
            external_id=f"rss_{raw_data['id']}",
            title=raw_data['title'],
            description=raw_data.get('summary'),
            data={
                "link": raw_data.get('link'),
                "published_at": raw_data.get('published')
            }
        )
