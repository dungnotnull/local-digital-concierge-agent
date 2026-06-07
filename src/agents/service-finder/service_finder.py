import logging
from typing import List, Dict, Any, Optional
import aiohttp
import asyncio
from src.database.db_client import db
from src.models import ServiceProvider
from math import radians, cos, sin, asin, sqrt

logger = logging.getLogger(__name__)

class ServiceFinder:
    def __init__(self):
        # OSM category to tags mapping
        self.OSM_CATEGORY_TAGS = {
            'plumbing': ['craft=plumber', 'shop=plumber'],
            'electrical': ['craft=electrician', 'shop=electrical'],
            'hvac': ['craft=hvac', 'shop=hvac'],
            'appliance': ['shop=appliance', 'repair=appliance'],
            'structural': ['craft=builder', 'shop=hardware'],
            'pest_control': ['shop=pest_control'],
            'cleaning': ['shop=cleaning'],
            'other': []
        }
    
    async def search_providers(self, issue_description: str, home_lat: float, home_lng: float, radius_km: float = 3.0) -> List[ServiceProvider]:
        """
        Search for service providers based on issue description and location.
        Returns a list of ServiceProvider objects sorted by relevance.
        """
        # Step 1: Classify the issue to get category and urgency
        category, urgency, keywords = await self._classify_issue(issue_description)
        
        # Step 2: Get trusted providers from DB (trust_level >= 2)
        trusted_providers = await self._get_trusted_providers(category)
        
        # Step 3: Search OSM for providers in the area
        osm_providers = await self._search_osm(category, home_lat, home_lng, radius_km)
        
        # Step 4: Combine and deduplicate (by name and phone)
        all_providers = self._merge_providers(trusted_providers, osm_providers)
        
        # Step 5: Rank providers
        ranked_providers = self._rank_providers(all_providers, home_lat, home_lng)
        
        return ranked_providers
    
    async def _classify_issue(self, issue_description: str) -> tuple[str, str, List[str]]:
        """Classify issue using LLM or fallback."""
        # For now, we'll use a simple keyword-based fallback.
        # In production, we would call the LLM with the issue-classifier prompt.
        issue_lower = issue_description.lower()
        if any(word in issue_lower for word in ['vòi', 'nước', 'rò', 'ró', 'ránh', 'cáp', 'báy']):
            category = 'plumbing'
        elif any(word in issue_lower for word in ['điện', 'b� t', 'công', 't?', 'điện thoại', 'mệy']):
            category = 'electrical'
        elif any(word in issue_lower for word in ['máy điều hòa', 'l� m', 'giờ', 'kh?�ng làm']):
            category = 'hvac'
        elif any(word in issue_lower for word in ['tịnh', 'mểy', 'băng', 'chĻnh']):
            category = 'appliance'
        elif any(word in issue_lower for word in ['của', 'của', 'b?�ng', 'l?�']):
            category = 'structural'
        elif any(word in issue_lower for word in ['côn trưng', 'chuột', 'chuot']):
            category = 'pest_control'
        elif any(word in issue_lower for word in ['v? sinh', 'dược', 'quăt']):
            category = 'cleaning'
        else:
            category = 'other'
        
        # Determine urgency (simplified)
        urgency = 'normal'
        if any(word in issue_lower for word in ['g?�s rò', 'ló', 'chọng', 'ộn']):
            urgency = 'emergency'
        elif any(word in issue_lower for word in ['kh?�ng quan trộng', 'thư�ng xuy?�n']):
            urgency = 'low'
        
        keywords = [word for word in issue_lower.split() if len(word) > 3][:5]
        return category, urgency, keywords
    
    async def _get_trusted_providers(self, category: str) -> List[ServiceProvider]:
        """Get trusted providers from the local database."""
        rows = await db.fetch_all(
            """SELECT * FROM service_providers 
               WHERE category = ? AND trust_level >= 2
               ORDER BY trust_level DESC, rating DESC""",
            (category,)
        )
        providers = []
        for row in rows:
            providers.append(ServiceProvider(
                id=row[0],
                name=row[1],
                category=row[2],
                phone=row[3],
                address=row[4],
                latitude=row[5],
                longitude=row[6],
                distance_meters=row[7],
                trust_level=row[8],
                rating=row[9],
                notes=row[10],
                times_used=row[11],
                last_used=row[12],
                is_favorite=bool(row[13]),
                source=row[14],
                created_at=row[15],
                updated_at=row[16]
            ))
        return providers
    
    async def _search_osm(self, category: str, lat: float, lng: float, radius_km: float) -> List[ServiceProvider]:
        """Search OpenStreetMap for providers in the given category and area."""
        tags = self.OSM_CATEGORY_TAGS.get(category, [])
        if not tags:
            return []
        
        # Build Overpass QL query
        # We'll search for nodes, ways, relations with the given tags within radius
        # Using the Overpass API's "around" filter
        tag_filter = ' or '.join(tags)
        query = f"""
        [out:json][timeout:25];
        (
          node["{tag_filter}"](around:{radius_km*1000},{lat},{lng});
          way["{tag_filter}"](around:{radius_km*1000},{lat},{lng});
          relation["{tag_filter}"](around:{radius_km*1000},{lat},{lng});
        );
        out center;
        """
        
        url = "https://overpass-api.de/api/interpreter"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=query) as resp:
                    if resp.status != 200:
                        logger.warning(f"OSM request failed with status {resp.status}")
                        return []
                    data = await resp.json()
            providers = []
            for element in data.get('elements', []):
                # Get latitude and longitude
                if 'lat' in element and 'lon' in element:
                    plat = element['lat']
                    plng = element['lon']
                elif 'center' in element:
                    plat = element['center']['lat']
                    plng = element['center']['lon']
                else:
                    continue
                
                # Calculate distance
                distance = self._haversine_distance(lat, lng, plat, plng)
                
                # Extract name and other details from tags
                tags = element.get('tags', {})
                name = tags.get('name') or tags.get('operator') or 'Unknown'
                if not name or name == 'Unknown':
                    continue
                
                provider = ServiceProvider(
                    name=name,
                    category=category,
                    phone=tags.get('phone'),
                    address=tags.get('addr:full') or tags.get('addr:street'),
                    latitude=plat,
                    longitude=plng,
                    distance_meters=distance,
                    trust_level=0,  # OSM providers start as unknown
                    rating=float(tags.get('rating', 0)) if tags.get('rating') else None,
                    notes=tags.get('notes'),
                    source='osm'
                )
                providers.append(provider)
            return providers
        except Exception as e:
            logger.error(f"Error searching OSM: {e}")
            return []
    
    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in meters."""
        # Convert decimal degrees to radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        # Radius of earth in meters
        r = 6371000
        return c * r
    
    def _merge_providers(self, trusted: List[ServiceProvider], osm: List[ServiceProvider]) -> List[ServiceProvider]:
        """Merge trusted and OSM providers, preferring trusted ones and deduplicating by name."""
        # Create a dict keyed by normalized name
        merged = {}
        for provider in trusted:
            key = provider.name.lower().strip()
            merged[key] = provider
        
        for provider in osm:
            key = provider.name.lower().strip()
            if key not in merged:
                merged[key] = provider
            # If already present (from trusted), we keep the trusted one (higher trust level)
        return list(merged.values())
    
    def _rank_providers(self, providers: List[ServiceProvider], home_lat: float, home_lng: float) -> List[ServiceProvider]:
        """Rank providers by trust level, rating, and distance."""
        def score(p: ServiceProvider) -> float:
            # Trust level is most important
            trust_score = p.trust_level * 30  # 0, 30, 60, 90
            
            # Rating from public sources (0-5 scale)
            rating_score = (p.rating or 3.0) * 5  # 0-25
            
            # Distance penalty (closer is better)
            # Update distance if not already set
            if p.distance_meters is None and p.latitude is not None and p.longitude is not None:
                p.distance_meters = self._haversine_distance(home_lat, home_lng, p.latitude, p.longitude)
            distance_penalty = min(p.distance_meters or 0, 5000) / 1000 * 2  # 0-10 for 0-5km
            
            # Freshness: providers with recent usage get a boost
            usage_score = min(p.times_used or 0, 10)  # 0-10
            
            return trust_score + rating_score - distance_penalty + usage_score
        
        return sorted(providers, key=score, reverse=True)
