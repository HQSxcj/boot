# services/keyword_store.py
# 识别词累积存储服务

import json
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_


class KeywordStore:
    """Service for managing accumulated recognition keywords."""
    
    def __init__(self, session_factory):
        """
        Initialize KeywordStore.
        
        Args:
            session_factory: SQLAlchemy session factory
        """
        self.session_factory = session_factory
    
    def add_keyword(self, keyword: str, normalized: str, media_type: str = 'movie',
                    tmdb_id: str = None, source: str = 'ai', extra_info: Dict = None) -> Dict[str, Any]:
        """
        Add or update a recognition keyword.
        
        If keyword already exists, increment match_count.
        
        Args:
            keyword: Original filename keyword
            normalized: Normalized title name
            media_type: 'movie' or 'tv'
            tmdb_id: Optional TMDB ID
            source: Source of the keyword (ai/manual/import)
            extra_info: Optional extra info dict
            
        Returns:
            Result dict with success status and data
        """
        from models.recognition_keyword import RecognitionKeyword
        
        session = self.session_factory()
        try:
            # Check if keyword already exists
            existing = session.query(RecognitionKeyword).filter(
                RecognitionKeyword.keyword == keyword
            ).first()
            
            if existing:
                # Update existing record
                existing.match_count += 1
                if normalized and normalized != existing.normalized:
                    existing.normalized = normalized
                if tmdb_id:
                    existing.tmdb_id = tmdb_id
                if extra_info:
                    existing.extra_info = json.dumps(extra_info, ensure_ascii=False)
                session.commit()
                return {'success': True, 'data': existing.to_dict(), 'created': False}
            else:
                # Create new record
                new_keyword = RecognitionKeyword(
                    keyword=keyword,
                    normalized=normalized,
                    media_type=media_type,
                    tmdb_id=tmdb_id,
                    source=source,
                    extra_info=json.dumps(extra_info, ensure_ascii=False) if extra_info else None
                )
                session.add(new_keyword)
                session.commit()
                session.refresh(new_keyword)
                return {'success': True, 'data': new_keyword.to_dict(), 'created': True}
        except Exception as e:
            session.rollback()
            return {'success': False, 'error': str(e)}
        finally:
            session.close()
    
    def find_keyword(self, keyword: str) -> Optional[Dict[str, Any]]:
        """
        Find an exact keyword match.
        
        Args:
            keyword: The keyword to search for
            
        Returns:
            Keyword dict or None
        """
        from models.recognition_keyword import RecognitionKeyword
        
        session = self.session_factory()
        try:
            result = session.query(RecognitionKeyword).filter(
                RecognitionKeyword.keyword == keyword
            ).first()
            return result.to_dict() if result else None
        finally:
            session.close()
    
    def search_keywords(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search keywords by partial match.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of matching keywords
        """
        from models.recognition_keyword import RecognitionKeyword
        
        session = self.session_factory()
        try:
            results = session.query(RecognitionKeyword).filter(
                or_(
                    RecognitionKeyword.keyword.ilike(f'%{query}%'),
                    RecognitionKeyword.normalized.ilike(f'%{query}%')
                )
            ).order_by(RecognitionKeyword.match_count.desc()).limit(limit).all()
            return [r.to_dict() for r in results]
        finally:
            session.close()
    
    def get_most_used(self, limit: int = 50, media_type: str = None) -> List[Dict[str, Any]]:
        """
        Get the most frequently matched keywords.
        
        Args:
            limit: Maximum results
            media_type: Optional filter by type
            
        Returns:
            List of top keywords
        """
        from models.recognition_keyword import RecognitionKeyword
        
        session = self.session_factory()
        try:
            query = session.query(RecognitionKeyword)
            if media_type:
                query = query.filter(RecognitionKeyword.media_type == media_type)
            results = query.order_by(RecognitionKeyword.match_count.desc()).limit(limit).all()
            return [r.to_dict() for r in results]
        finally:
            session.close()
    
    def delete_keyword(self, keyword_id: int) -> Dict[str, Any]:
        """
        Delete a keyword by ID.
        
        Args:
            keyword_id: The keyword ID to delete
            
        Returns:
            Result dict
        """
        from models.recognition_keyword import RecognitionKeyword
        
        session = self.session_factory()
        try:
            keyword = session.query(RecognitionKeyword).filter(
                RecognitionKeyword.id == keyword_id
            ).first()
            if keyword:
                session.delete(keyword)
                session.commit()
                return {'success': True, 'message': 'Keyword deleted'}
            return {'success': False, 'error': 'Keyword not found'}
        except Exception as e:
            session.rollback()
            return {'success': False, 'error': str(e)}
        finally:
            session.close()
    
    def bulk_import(self, keywords: List[Dict[str, str]], source: str = 'import') -> Dict[str, Any]:
        """
        Bulk import keywords from a list.
        
        Args:
            keywords: List of dicts with 'keyword' and 'normalized' keys
            source: Source identifier
            
        Returns:
            Result dict with counts
        """
        added = 0
        updated = 0
        errors = []
        
        for kw in keywords:
            try:
                result = self.add_keyword(
                    keyword=kw.get('keyword', ''),
                    normalized=kw.get('normalized', ''),
                    media_type=kw.get('mediaType', 'movie'),
                    tmdb_id=kw.get('tmdbId'),
                    source=source
                )
                if result.get('success'):
                    if result.get('created'):
                        added += 1
                    else:
                        updated += 1
                else:
                    errors.append(kw.get('keyword', ''))
            except Exception as e:
                errors.append(f"{kw.get('keyword', '')}: {str(e)}")
        
        return {
            'success': True,
            'added': added,
            'updated': updated,
            'errors': errors
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get keyword statistics.
        
        Returns:
            Stats dict
        """
        from models.recognition_keyword import RecognitionKeyword
        from sqlalchemy import func
        
        session = self.session_factory()
        try:
            total = session.query(func.count(RecognitionKeyword.id)).scalar()
            movie_count = session.query(func.count(RecognitionKeyword.id)).filter(
                RecognitionKeyword.media_type == 'movie'
            ).scalar()
            tv_count = session.query(func.count(RecognitionKeyword.id)).filter(
                RecognitionKeyword.media_type == 'tv'
            ).scalar()
            ai_count = session.query(func.count(RecognitionKeyword.id)).filter(
                RecognitionKeyword.source == 'ai'
            ).scalar()
            
            return {
                'total': total,
                'movie': movie_count,
                'tv': tv_count,
                'aiGenerated': ai_count,
                'manual': total - ai_count
            }
        finally:
            session.close()
