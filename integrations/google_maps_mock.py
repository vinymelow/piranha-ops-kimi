"""
Google Maps Mock - Simulador completo da Google Places API para encontrar estúdios de tatuagem
Baseado nas especificações do Input V4
"""

import asyncio
import json
import random
import time
import uuid
import re
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BusinessType(Enum):
    PROFESSIONAL = "professional"
    AMATEUR = "amateur"
    CHAIN = "chain"
    HOME_STUDIO = "home_studio"

class SocialPlatform(Enum):
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    TIKTOK = "tiktok"
    WEBSITE = "website"

@dataclass
class Review:
    id: str
    rating: float
    text: str
    author: str
    date: datetime
    helpful_count: int

@dataclass
class BusinessHours:
    monday: Optional[str] = None
    tuesday: Optional[str] = None
    wednesday: Optional[str] = None
    thursday: Optional[str] = None
    friday: Optional[str] = None
    saturday: Optional[str] = None
    sunday: Optional[str] = None

@dataclass
class ContactInfo:
    phone: str
    email: Optional[str] = None
    website: Optional[str] = None
    instagram: Optional[str] = None
    facebook: Optional[str] = None
    tiktok: Optional[str] = None

@dataclass
class Location:
    latitude: float
    longitude: float
    address: str
    city: str
    state: str
    country: str
    postal_code: str
    neighborhood: Optional[str] = None

@dataclass
class B2BScore:
    total_score: float
    business_age_score: float
    review_score: float
    website_score: float
    social_media_score: float
    location_score: float
    equipment_score: float
    client_potential_score: float
    factors: List[str]

@dataclass
class TattooStudio:
    """Classe completa representando um estúdio de tatuagem"""
    place_id: str
    name: str
    location: Location
    rating: float
    review_count: int
    reviews: List[Review]
    business_status: str
    contact: ContactInfo
    business_hours: BusinessHours
    photos: List[str]
    price_level: int  # 0-4 (gratuito a muito caro)
    types: List[str]
    business_type: BusinessType
    estimated_monthly_revenue: float
    artist_count: int
    specializations: List[str]
    equipment_quality: str  # low, medium, high, premium
    years_in_business: int
    b2b_score: Optional[B2BScore] = None
    last_updated: datetime = None
    
    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = datetime.now()

class GoogleMapsMock:
    """
    Simulador completo da Google Places API para encontrar estúdios de tatuagem
    Implementa todos os métodos especificados no Input V4
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.failure_rate = 0.02  # 2% de falhas
        self.min_delay = 0.5
        self.max_delay = 2.0
        
        # Templates de estúdios realistas por cidade
        self.studio_templates = self._load_studio_templates()
        
        # Cache de resultados
        self.cache: Dict[str, List[TattooStudio]] = {}
        
        # Configuração de persistência
        self.persistence_dir = Path("mock_data")
        self.persistence_dir.mkdir(exist_ok=True)
        
        logger.info("GoogleMapsMock inicializado com sucesso")
    
    def _load_studio_templates(self) -> Dict[str, List[Dict]]:
        """Carrega templates de estúdios realistas por cidade"""
        return {
            "lisboa": [
                {
                    "name_patterns": ["Ink", "Tattoo", "Studio", "Art", "Lisboa", "Portugal"],
                    "base_names": ["Lisboa Ink Studio", "Alfama Tattoo Art", "Baixa Tattoo Studio", 
                                  "Chiado Art Tattoo", "Bairro Alto Ink", "Portugal Tattoo Collective"],
                    "neighborhoods": ["Alfama", "Baixa", "Chiado", "Bairro Alto", "Príncipe Real", "Mouraria"],
                    "specializations": ["Realismo", "Old School", "Geometric", "Blackwork", "Minimalista"],
                    "price_range": (50, 200)
                }
            ],
            "porto": [
                {
                    "name_patterns": ["Porto", "Tattoo", "Ink", "Studio", "Norte"],
                    "base_names": ["Porto Tattoo Studio", "Invicta Ink", "Ribeira Art Tattoo", 
                                  "Gaia Tattoo Collective", "Norte Tattoo Studio", "Douro Ink Art"],
                    "neighborhoods": ["Ribeira", "Baixa", "Foz", "Boavista", "Cedofeita", "Miragaia"],
                    "specializations": ["Tradicional", "Neo Tradicional", "Black & Grey", "Pontilhismo", "Watercolor"],
                    "price_range": (40, 180)
                }
            ],
            "far": [
                {
                    "name_patterns": ["Faro", "Algarve", "Tattoo", "Studio", "South"],
                    "base_names": ["Faro Tattoo Studio", "Algarve Ink", "Sul Tattoo Art", 
                                  "Praia Tattoo Collective", "Ria Formosa Studio", "Algarve Art Tattoo"],
                    "neighborhoods": ["Centro", "Alameda", "Montenegro", "Sé", "Vila-Adentro", "Bom João"],
                    "specializations": ["Tribal", "Maori", "Blackwork", "Geométrico", "Realismo"],
                    "price_range": (45, 170)
                }
            ],
            "madrid": [
                {
                    "name_patterns": ["Madrid", "Tattoo", "Ink", "Studio", "Spain"],
                    "base_names": ["Madrid Tattoo Studio", "Capital Ink", "Gran Vía Tattoo", 
                                  "Sol Art Tattoo", "Latina Studio", "España Tattoo Collective"],
                    "neighborhoods": ["Centro", "Sol", "Gran Vía", "Latina", "Chueca", "Malasaña"],
                    "specializations": ["Realismo", "Old School", "Japonês", "Blackwork", "Minimalista"],
                    "price_range": (60, 250)
                }
            ],
            "barcelona": [
                {
                    "name_patterns": ["Barcelona", "Tattoo", "Ink", "Studio", "Catalunya"],
                    "base_names": ["Barcelona Tattoo Studio", "Catalan Ink", "Gaudí Tattoo Art", 
                                  "Rambla Tattoo Collective", "Gótico Studio", "Catalunya Art Tattoo"],
                    "neighborhoods": ["Gótico", "Raval", "Eixample", "Gràcia", "Born", "Barceloneta"],
                    "specializations": ["Modernista", "Geométrico", "Blackwork", "Realismo", "Watercolor"],
                    "price_range": (70, 300)
                }
            ]
        }
    
    def _simulate_delay(self):
        """Simula delay realista da API"""
        delay = random.uniform(self.min_delay, self.max_delay)
        time.sleep(delay)
    
    def _should_fail(self) -> bool:
        """Determina se uma requisição deve falhar (2% de chance)"""
        return random.random() < self.failure_rate
    
    def _generate_place_id(self) -> str:
        """Gera ID único para lugar"""
        return f"{random.randint(1000000000, 9999999999)}"
    
    def _generate_coordinates(self, city: str) -> Tuple[float, float]:
        """Gera coordenadas realistas para cada cidade"""
        coordinates = {
            "lisboa": (38.7223, -9.1393),
            "porto": (41.1579, -8.6291),
            "faro": (37.0194, -7.9323),
            "madrid": (40.4168, -3.7038),
            "barcelona": (41.3851, 2.1734)
        }
        
        base_lat, base_lng = coordinates.get(city.lower(), (40.0, 0.0))
        
        # Adiciona variação realista
        lat_variation = random.uniform(-0.05, 0.05)
        lng_variation = random.uniform(-0.05, 0.05)
        
        return (base_lat + lat_variation, base_lng + lng_variation)
    
    def _detect_business_type(self, studio_data: Dict) -> BusinessType:
        """Detecta tipo de negócio baseado em vários fatores"""
        name = studio_data.get("name", "").lower()
        review_count = studio_data.get("review_count", 0)
        rating = studio_data.get("rating", 0)
        
        # Detecta cadeias
        chain_indicators = ["collective", "group", "chain", "studio network"]
        if any(indicator in name for indicator in chain_indicators):
            return BusinessType.CHAIN
        
        # Detecta home studios
        home_indicators = ["home", "residencial", "apartamento", "casa"]
        if any(indicator in name for indicator in home_indicators):
            return BusinessType.HOME_STUDIO
        
        # Detecta profissionais vs amadores
        if review_count > 100 and rating > 4.0:
            return BusinessType.PROFESSIONAL
        elif review_count < 20 or rating < 3.5:
            return BusinessType.AMATEUR
        else:
            return BusinessType.PROFESSIONAL
    
    def _detect_website_quality(self, website: Optional[str]) -> float:
        """Detecta se website é profissional ou amador (0-1)"""
        if not website:
            return 0.0
        
        score = 0.0
        
        # Domínio próprio
        if not any(platform in website for platform in ["wix.com", "wordpress.com", "blogspot.com", "weebly.com"]):
            score += 0.3
        
        # Presença de HTTPS
        if website.startswith("https://"):
            score += 0.2
        
        # Extensões profissionais
        professional_extensions = [".com", ".pt", ".es", ".eu", ".studio", ".tattoo"]
        if any(ext in website for ext in professional_extensions):
            score += 0.2
        
        # Nome do estúdio no domínio
        studio_name_indicators = ["tattoo", "ink", "studio", "art"]
        if any(indicator in website.lower() for indicator in studio_name_indicators):
            score += 0.3
        
        return min(score, 1.0)
    
    def _estimate_business_age(self, reviews: List[Review]) -> int:
        """Estima idade do negócio baseada em reviews"""
        if not reviews:
            return 0
        
        # Ordena reviews por data
        sorted_reviews = sorted(reviews, key=lambda x: x.date)
        
        # Pega a data mais antiga
        oldest_review = sorted_reviews[0].date
        current_date = datetime.now()
        
        # Calcula diferença em anos
        age_years = (current_date - oldest_review).days / 365.25
        
        return max(0, int(age_years))
    
    def _enrich_contact_info(self, contact: ContactInfo, studio_name: str) -> ContactInfo:
        """Enriquece informações de contato com email e redes sociais"""
        # Gera email se não existir
        if not contact.email:
            # Remove caracteres especiais do nome
            clean_name = re.sub(r'[^\w\s]', '', studio_name.lower().replace(" ", ""))
            domains = ["@gmail.com", "@hotmail.com", "@outlook.com", ".studio@outlook.com", "@tattoo.pt"]
            domain = random.choice(domains)
            contact.email = f"{clean_name}{random.randint(1, 999)}{domain}"
        
        # Enriquece redes sociais
        if not contact.instagram:
            clean_handle = re.sub(r'[^\w\s]', '', studio_name.lower().replace(" ", "_"))
            contact.instagram = f"@{clean_handle}_tattoo"
        
        if not contact.facebook and random.random() > 0.3:
            clean_handle = re.sub(r'[^\w\s]', '', studio_name.lower().replace(" ", ""))
            contact.facebook = f"facebook.com/{clean_handle}tattoo"
        
        if not contact.tiktok and random.random() > 0.6:
            clean_handle = re.sub(r'[^\w\s]', '', studio_name.lower().replace(" ", ""))
            contact.tiktok = f"@{clean_handle}_ink"
        
        return contact
    
    def _calculate_b2b_score(self, studio: TattooStudio) -> B2BScore:
        """Calcula score B2B completo com base em múltiplos fatores"""
        factors = []
        
        # 1. Idade do negócio (0-20 pontos)
        if studio.years_in_business >= 5:
            business_age_score = 20.0
            factors.append("Negócio estabelecido (5+ anos)")
        elif studio.years_in_business >= 2:
            business_age_score = 15.0
            factors.append("Negócio em crescimento (2-4 anos)")
        elif studio.years_in_business >= 1:
            business_age_score = 10.0
            factors.append("Negócio novo (1-2 anos)")
        else:
            business_age_score = 5.0
            factors.append("Negócio muito recente")
        
        # 2. Score de reviews (0-25 pontos)
        review_quality_score = min(studio.rating * 5, 25.0)  # 5.0 rating = 25 pontos
        if studio.review_count > 200:
            review_volume_bonus = 10.0
            factors.append("Alto volume de reviews")
        elif studio.review_count > 100:
            review_volume_bonus = 5.0
            factors.append("Volume moderado de reviews")
        else:
            review_volume_bonus = 0.0
            factors.append("Baixo volume de reviews")
        
        review_score = review_quality_score + review_volume_bonus
        
        # 3. Website score (0-20 pontos)
        website_score = self._detect_website_quality(studio.contact.website) * 20
        if website_score > 15:
            factors.append("Website profissional")
        elif website_score > 10:
            factors.append("Website básico")
        else:
            factors.append("Sem website profissional")
        
        # 4. Social media score (0-15 pontos)
        social_count = 0
        if studio.contact.instagram:
            social_count += 1
        if studio.contact.facebook:
            social_count += 1
        if studio.contact.tiktok:
            social_count += 1
        
        social_media_score = (social_count / 3) * 15
        if social_count >= 2:
            factors.append("Fort presença em redes sociais")
        elif social_count == 1:
            factors.append("Presença limitada em redes sociais")
        else:
            factors.append("Sem presença em redes sociais")
        
        # 5. Location score (0-10 pontos)
        if studio.location.neighborhood in ["Centro", "Baixa", "Downtown"]:
            location_score = 10.0
            factors.append("Localização premium")
        elif any(word in studio.location.neighborhood.lower() for word in ["comercial", "business"]):
            location_score = 8.0
            factors.append("Localização comercial")
        else:
            location_score = 6.0
            factors.append("Localização padrão")
        
        # 6. Equipment score (0-5 pontos)
        equipment_scores = {
            "premium": 5.0,
            "high": 4.0,
            "medium": 3.0,
            "low": 1.0
        }
        equipment_score = equipment_scores.get(studio.equipment_quality, 2.0)
        factors.append(f"Equipamento: {studio.equipment_quality}")
        
        # 7. Client potential score (0-5 pontos)
        if studio.estimated_monthly_revenue > 15000:
            client_potential_score = 5.0
            factors.append("Alto potencial de cliente")
        elif studio.estimated_monthly_revenue > 8000:
            client_potential_score = 3.0
            factors.append("Potencial médio de cliente")
        else:
            client_potential_score = 1.0
            factors.append("Potencial básico de cliente")
        
        # Calcula score total
        total_score = (business_age_score + review_score + website_score + 
                      social_media_score + location_score + equipment_score + 
                      client_potential_score)
        
        # Normaliza para 0-100
        total_score = min(total_score, 100.0)
        
        return B2BScore(
            total_score=total_score,
            business_age_score=business_age_score,
            review_score=review_score,
            website_score=website_score,
            social_media_score=social_media_score,
            location_score=location_score,
            equipment_score=equipment_score,
            client_potential_score=client_potential_score,
            factors=factors
        )
    
    def _generate_studio_variation(self, template: Dict, city: str, index: int) -> TattooStudio:
        """Gera variação única de estúdio baseada em template"""
        # Gera coordenadas
        lat, lng = self._generate_coordinates(city)
        
        # Seleciona nome base
        base_name = random.choice(template["base_names"])
        
        # Adiciona variação ao nome
        variation = random.choice(["", " Studio", " Art", " Ink", " Collective", " Tattoo"])
        studio_name = f"{base_name}{variation}"
        
        # Seleciona bairro
        neighborhood = random.choice(template["neighborhoods"])
        
        # Gera endereço realista
        street_types = ["Rua", "Avenida", "Travessa", "Largo", "Praça"]
        street_names = ["da Liberdade", "do Comércio", "Principal", "Central", "de São Paulo",
                       "das Flores", "do Sol", "da Alegria", "da Paz", "dos Artistas"]
        
        street = f"{random.choice(street_types)} {random.choice(street_names)}"
        number = random.randint(1, 999)
        
        address = f"{street}, {number}, {neighborhood}"
        
        # Gera reviews realistas
        review_count = random.randint(5, 350)
        rating = round(random.uniform(3.5, 5.0), 1)
        
        reviews = []
        for i in range(min(review_count, 50)):  # Limita a 50 reviews no máximo
            review_date = datetime.now() - timedelta(days=random.randint(1, 1095))  # Últimos 3 anos
            
            review_texts = [
                "Excelente trabalho! Profissionais muito qualificados.",
                "Ambiente limpo e acolhedor. Recomendo!",
                "Ótima experiência, voltarei com certeza.",
                "Artistas talentosos e preços justos.",
                "Muito satisfeito com o resultado final.",
                "Studio profissional, equipe atenciosa.",
                "Trabalho impecável, superou expectativas.",
                "Local bem localizado e fácil de encontrar.",
                "Preços competitivos para a qualidade oferecida.",
                "Atendimento personalizado e profissional."
            ]
            
            review = Review(
                id=f"review_{i}_{uuid.uuid4().hex[:8]}",
                rating=random.choice([4.0, 4.5, 5.0]) if random.random() > 0.2 else random.choice([3.0, 3.5]),
                text=random.choice(review_texts),
                author=f"Cliente {random.randint(1000, 9999)}",
                date=review_date,
                helpful_count=random.randint(0, 15)
            )
            reviews.append(review)
        
        # Gera contato
        phone_codes = {
            "lisboa": "+351 21",
            "porto": "+351 22",
            "faro": "+351 28",
            "madrid": "+34 91",
            "barcelona": "+34 93"
        }
        
        phone_code = phone_codes.get(city.lower(), "+351 21")
        phone = f"{phone_code} {random.randint(1000000, 9999999)}"
        
        # Gera website
        website = None
        if random.random() > 0.3:  # 70% chance de ter website
            clean_name = re.sub(r'[^\w\s]', '', studio_name.lower().replace(" ", ""))
            website_types = [
                f"https://www.{clean_name}.com",
                f"https://{clean_name}.wixsite.com/studio",
                f"https://{clean_name}.wordpress.com",
                f"https://www.{clean_name}.pt"
            ]
            website = random.choice(website_types)
        
        contact = ContactInfo(
            phone=phone,
            website=website
        )
        
        # Enriquece contato
        contact = self._enrich_contact_info(contact, studio_name)
        
        # Gera horários de funcionamento
        business_hours = BusinessHours()
        if random.random() > 0.2:  # 80% têm horários definidos
            days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
            for day in days[:5]:  # Segunda a sexta
                open_time = f"{random.randint(9, 11)}:00 AM"
                close_time = f"{random.randint(18, 21)}:00 PM"
                setattr(business_hours, day, f"{open_time} - {close_time}")
            
            # Sábado
            if random.random() > 0.3:
                sat_open = f"{random.randint(9, 11)}:00 AM"
                sat_close = f"{random.randint(16, 19)}:00 PM"
                business_hours.saturday = f"{sat_open} - {sat_close}"
            
            # Domingo
            if random.random() > 0.7:
                sun_open = f"{random.randint(10, 12)}:00 AM"
                sun_close = f"{random.randint(16, 18)}:00 PM"
                business_hours.sunday = f"{sun_open} - {sun_close}"
        
        # Estima idade do negócio
        years_in_business = self._estimate_business_age(reviews)
        
        # Detecta tipo de negócio
        business_type = self._detect_business_type({
            "name": studio_name,
            "review_count": review_count,
            "rating": rating
        })
        
        # Estima receita mensal
        price_min, price_max = template["price_range"]
        avg_price = (price_min + price_max) / 2
        estimated_clients = random.randint(20, 150)
        estimated_monthly_revenue = avg_price * estimated_clients
        
        # Número de artistas
        artist_count = random.randint(1, 8)
        if business_type == BusinessType.CHAIN:
            artist_count = random.randint(5, 15)
        
        # Qualidade de equipamento
        equipment_qualities = ["low", "medium", "high", "premium"]
        equipment_weights = [0.1, 0.4, 0.4, 0.1]  # Mais chances de médio/alto
        equipment_quality = random.choices(equipment_qualities, weights=equipment_weights)[0]
        
        # Cria estúdio
        studio = TattooStudio(
            place_id=self._generate_place_id(),
            name=studio_name,
            location=Location(
                latitude=lat,
                longitude=lng,
                address=address,
                city=city.title(),
                state="Lisbon" if city.lower() == "lisboa" else city.title(),
                country="Portugal" if city.lower() in ["lisboa", "porto", "faro"] else "Spain",
                postal_code=f"{random.randint(1000, 9999)}-{random.randint(100, 999)}",
                neighborhood=neighborhood
            ),
            rating=rating,
            review_count=review_count,
            reviews=reviews,
            business_status="OPERATIONAL",
            contact=contact,
            business_hours=business_hours,
            photos=[f"https://example.com/photo_{i}.jpg" for i in range(random.randint(0, 10))],
            price_level=random.randint(2, 4),
            types=["tattoo_shop", "beauty_salon", "point_of_interest", "establishment"],
            business_type=business_type,
            estimated_monthly_revenue=estimated_monthly_revenue,
            artist_count=artist_count,
            specializations=random.sample(template["specializations"], 
                                        random.randint(2, min(4, len(template["specializations"]))),
                                        ),
            equipment_quality=equipment_quality,
            years_in_business=years_in_business
        )
        
        # Calcula score B2B
        studio.b2b_score = self._calculate_b2b_score(studio)
        
        return studio
    
    def _deduplicate_studios(self, studios: List[TattooStudio]) -> List[TattooStudio]:
        """Remove duplicatas baseadas em nome e localização"""
        seen = set()
        unique_studios = []
        
        for studio in studios:
            # Cria chave única baseada em nome e coordenadas aproximadas
            lat_key = round(studio.location.latitude, 3)
            lng_key = round(studio.location.longitude, 3)
            name_key = studio.name.lower().replace(" ", "")
            
            key = f"{name_key}_{lat_key}_{lng_key}"
            
            if key not in seen:
                seen.add(key)
                unique_studios.append(studio)
        
        return unique_studios
    
    def _check_existing_clients(self, studios: List[TattooStudio], 
                               existing_client_ids: List[str]) -> List[TattooStudio]:
        """Remove estúdios que já são clientes"""
        if not existing_client_ids:
            return studios
        
        return [
            studio for studio in studios 
            if studio.place_id not in existing_client_ids
        ]
    
    async def search_studios(self, 
                           location: str, 
                           radius: int = 5000,
                           min_rating: float = 0.0,
                           max_results: int = 20,
                           language: str = "pt-BR",
                           existing_client_ids: Optional[List[str]] = None,
                           min_b2b_score: Optional[float] = None) -> Dict[str, Any]:
        """
        Busca estúdios de tatuagem em uma localização
        
        Args:
            location: Cidade ou coordenadas (ex: "Lisboa" ou "40.7128,-74.0060")
            radius: Raio de busca em metros (máximo 50000)
            min_rating: Rating mínimo (0-5)
            max_results: Número máximo de resultados
            language: Idioma dos resultados
            existing_client_ids: IDs de clientes existentes para filtrar
            min_b2b_score: Score B2B mínimo para filtrar resultados
            
        Returns:
            Dict com resultados da busca
        """
        logger.info(f"Buscando estúdios em: {location}")
        
        # Simula delay da API
        self._simulate_delay()
        
        # Simula falha ocasional
        if self._should_fail():
            return {
                "success": False,
                "error": "Erro na API do Google Maps",
                "error_code": "MAPS_API_ERROR"
            }
        
        # Parse da localização
        if "," in location:
            # Coordenadas fornecidas
            try:
                lat, lng = map(float, location.split(","))
                city = "unknown"
            except ValueError:
                return {
                    "success": False,
                    "error": "Formato de coordenadas inválido",
                    "error_code": "INVALID_COORDINATES"
                }
        else:
            # Nome da cidade
            city = location.lower().strip()
            if city not in self.studio_templates:
                return {
                    "success": False,
                    "error": f"Cidade não suportada: {location}",
                    "error_code": "CITY_NOT_SUPPORTED",
                    "supported_cities": list(self.studio_templates.keys())
                }
        
        # Verifica cache
        cache_key = f"{location}_{radius}_{min_rating}_{max_results}"
        if cache_key in self.cache:
            studios = self.cache[cache_key]
        else:
            # Gera estúdios
            studios = []
            template_list = self.studio_templates.get(city, self.studio_templates["lisboa"])
            
            for i in range(max_results):
                template = random.choice(template_list)
                studio = self._generate_studio_variation(template, city, i)
                
                # Aplica filtros básicos
                if studio.rating >= min_rating:
                    studios.append(studio)
            
            # Remove duplicatas
            studios = self._deduplicate_studios(studios)
            
            # Cacheia resultados
            self._cache_results(cache_key, studios)
        
        # Filtra clientes existentes
        if existing_client_ids:
            studios = self._check_existing_clients(studios, existing_client_ids)
        
        # Filtra por score B2B se especificado
        if min_b2b_score is not None:
            studios = [
                studio for studio in studios 
                if studio.b2b_score and studio.b2b_score.total_score >= min_b2b_score
            ]
        
        # Ordena por score B2B (melhores primeiro)
        studios.sort(key=lambda x: x.b2b_score.total_score if x.b2b_score else 0, reverse=True)
        
        # Limita resultados
        studios = studios[:max_results]
        
        # Converte para dict
        studios_data = []
        for studio in studios:
            studio_dict = asdict(studio)
            
            # Converte objetos complexos para dict
            studio_dict['location'] = asdict(studio.location)
            studio_dict['contact'] = asdict(studio.contact)
            studio_dict['business_hours'] = asdict(studio.business_hours)
            studio_dict['reviews'] = [asdict(review) for review in studio.reviews[:5]]  # Limita reviews
            
            if studio.b2b_score:
                studio_dict['b2b_score'] = asdict(studio.b2b_score)
            
            # Converte datetime para string
            studio_dict['last_updated'] = studio.last_updated.isoformat()
            for review in studio_dict['reviews']:
                review['date'] = review['date'].isoformat()
            
            studios_data.append(studio_dict)
        
        return {
            "success": True,
            "location": location,
            "radius": radius,
            "total_results": len(studios_data),
            "studios": studios_data,
            "timestamp": datetime.now().isoformat()
        }
    
    def _cache_results(self, cache_key: str, studios: List[TattooStudio]):
        """Cacheia resultados para performance"""
        self.cache[cache_key] = studios
        
        # Limpa cache antigo
        if len(self.cache) > 100:
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
    
    def get_studio_details(self, place_id: str) -> Dict[str, Any]:
        """
        Obtém detalhes completos de um estúdio específico
        
        Args:
            place_id: ID do lugar
            
        Returns:
            Dict com detalhes do estúdio
        """
        logger.info(f"Obtendo detalhes do estúdio: {place_id}")
        
        # Simula delay
        self._simulate_delay()
        
        # Procura em cache
        for cached_studios in self.cache.values():
            for studio in cached_studios:
                if studio.place_id == place_id:
                    studio_dict = asdict(studio)
                    studio_dict['location'] = asdict(studio.location)
                    studio_dict['contact'] = asdict(studio.contact)
                    studio_dict['business_hours'] = asdict(studio.business_hours)
                    studio_dict['reviews'] = [asdict(review) for review in studio.reviews]
                    
                    if studio.b2b_score:
                        studio_dict['b2b_score'] = asdict(studio.b2b_score)
                    
                    studio_dict['last_updated'] = studio.last_updated.isoformat()
                    for review in studio_dict['reviews']:
                        review['date'] = review['date'].isoformat()
                    
                    return {
                        "success": True,
                        "studio": studio_dict
                    }
        
        return {
            "success": False,
            "error": "Estúdio não encontrado",
            "error_code": "STUDIO_NOT_FOUND"
        }
    
    def get_supported_cities(self) -> Dict[str, Any]:
        """
        Obtém lista de cidades suportadas
        
        Returns:
            Dict com cidades suportadas
        """
        return {
            "success": True,
            "cities": list(self.studio_templates.keys()),
            "total": len(self.studio_templates)
        }
    
    def clear_cache(self) -> Dict[str, Any]:
        """
        Limpa cache de resultados
        
        Returns:
            Dict com confirmação
        """
        self.cache.clear()
        return {
            "success": True,
            "message": "Cache limpo com sucesso"
        }


# Funções utilitárias
async def create_google_maps_mock(config: Optional[Dict] = None) -> GoogleMapsMock:
    """
    Factory function para criar instância do GoogleMapsMock
    
    Args:
        config: Configuração opcional
        
    Returns:
        Instância do GoogleMapsMock
    """
    return GoogleMapsMock(config)

async def test_google_maps_mock():
    """
    Função de teste para verificar funcionamento do mock
    """
    print("🧪 Iniciando testes do GoogleMapsMock...")
    
    # Cria instância
    mock = await create_google_maps_mock()
    
    # Testa cidades suportadas
    print("🌍 Testando cidades suportadas...")
    cities = mock.get_supported_cities()
    print(f"Cidades: {', '.join(cities['cities'])}")
    
    # Testa busca em Lisboa
    print("📍 Testando busca em Lisboa...")
    results = await mock.search_studios(
        location="lisboa",
        max_results=5,
        min_rating=4.0
    )
    
    if results['success']:
        print(f"✅ Encontrados {results['total_results']} estúdios")
        
        # Mostra primeiro estúdio
        if results['studios']:
            studio = results['studios'][0]
            print(f"🏪 Primeiro estúdio: {studio['name']}")
            print(f"📊 Rating: {studio['rating']} ({studio['review_count']} reviews)")
            print(f"💰 Receita estimada: €{studio['estimated_monthly_revenue']:,.0f}/mês")
            print(f"⭐ Score B2B: {studio['b2b_score']['total_score']:.1f}/100")
            print(f"📱 Website: {studio['contact']['website'] or 'N/A'}")
            print(f"📸 Instagram: {studio['contact']['instagram'] or 'N/A'}")
            
            # Testa detalhes do estúdio
            print("🔍 Testando detalhes do estúdio...")
            details = mock.get_studio_details(studio['place_id'])
            if details['success']:
                print("✅ Detalhes obtidos com sucesso")
            else:
                print(f"❌ Erro ao obter detalhes: {details['error']}")
    else:
        print(f"❌ Erro na busca: {results['error']}")
    
    # Testa busca com filtros B2B
    print("🎯 Testando busca com filtros B2B...")
    b2b_results = await mock.search_studios(
        location="barcelona",
        max_results=3,
        min_b2b_score=70.0
    )
    
    if b2b_results['success']:
        print(f"✅ Encontrados {b2b_results['total_results']} estúdios com score B2B >= 70")
        for studio in b2b_results['studios']:
            print(f"  - {studio['name']}: Score {studio['b2b_score']['total_score']:.1f}")
    
    # Testa busca com clientes existentes
    print("🚫 Testando filtro de clientes existentes...")
    filtered_results = await mock.search_studios(
        location="porto",
        max_results=10,
        existing_client_ids=[results['studios'][0]['place_id']] if results['success'] else []
    )
    
    if filtered_results['success']:
        print(f"✅ Encontrados {filtered_results['total_results']} estúdios (filtrando clientes existentes)")
    
    print("✅ Testes concluídos!")


if __name__ == "__main__":
    # Executa testes se rodar diretamente
    asyncio.run(test_google_maps_mock())