# ==============================================================================
# proxy_manager.py — Residential Proxy Management
# ==============================================================================
# Purpose: Manage rotating residential proxies to avoid rate limiting
# ==============================================================================

import asyncio
import aiohttp
import random
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import logging
import os
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class ProxyProvider(Enum):
    BRIGHT_DATA = "bright_data"
    OXYLABS = "oxylabs"
    PROXYMESH = "proxymesh"
    STORM_PROXIES = "storm_proxies"
    TOR = "tor"
    PUBLIC = "public"

@dataclass
class ProxyConfig:
    """Configuration for proxy provider."""
    provider: ProxyProvider
    username: Optional[str] = None
    password: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    country: Optional[str] = None
    city: Optional[str] = None
    session_duration: int = 600  # 10 minutes
    max_requests_per_session: int = 100
    retry_attempts: int = 3
    timeout: int = 30

@dataclass
class ProxySession:
    """Represents an active proxy session."""
    proxy_url: str
    created_at: float
    request_count: int = 0
    last_used: float = 0
    success_count: int = 0
    failure_count: int = 0

class ProxyManager:
    """
    Manages rotating residential proxies to avoid rate limiting.
    Supports multiple providers with automatic fallback.
    """
    
    def __init__(self, config: ProxyConfig):
        self.config = config
        self.active_sessions: List[ProxySession] = []
        self.failed_proxies: Dict[str, float] = {}  # proxy_url -> failure_time
        self.proxy_blacklist_duration = 300  # 5 minutes
        self.max_concurrent_sessions = 5
        
        # Provider-specific configurations
        self.provider_configs = {
            ProxyProvider.BRIGHT_DATA: {
                'format': 'http://{username}-country-{country}-session-{session_id}:{password}@{host}:{port}',
                'session_id_length': 8
            },
            ProxyProvider.OXYLABS: {
                'format': 'http://{username}-country-{country}-session-{session_id}:{password}@{host}:{port}',
                'session_id_length': 6
            },
            ProxyProvider.PROXYMESH: {
                'format': 'http://{username}:{password}@{host}:{port}',
                'session_id_length': 0
            },
            ProxyProvider.STORM_PROXIES: {
                'format': 'http://{username}:{password}@{host}:{port}',
                'session_id_length': 0
            }
        }
    
    def _generate_session_id(self) -> str:
        """Generate a random session ID for proxy rotation."""
        import string
        length = self.provider_configs.get(self.config.provider, {}).get('session_id_length', 4)
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    
    def _build_proxy_url(self, session_id: Optional[str] = None) -> str:
        """Build proxy URL based on provider configuration."""
        if not self.config.host or not self.config.port:
            raise ValueError("Proxy host and port must be configured")
        
        provider_config = self.provider_configs.get(self.config.provider, {})
        format_str = provider_config.get('format', 'http://{username}:{password}@{host}:{port}')
        
        # Handle session-based providers
        if session_id and provider_config.get('session_id_length', 0) > 0:
            format_str = format_str.replace('{session_id}', session_id)
        
        # Handle country/city targeting
        if self.config.country:
            format_str = format_str.replace('{country}', self.config.country)
        else:
            format_str = format_str.replace('-country-{country}', '')
        
        return format_str.format(
            username=self.config.username or '',
            password=self.config.password or '',
            host=self.config.host,
            port=self.config.port,
            session_id=session_id or ''
        )
    
    async def get_proxy_session(self) -> Optional[ProxySession]:
        """Get an available proxy session, creating new ones as needed."""
        # Clean up expired sessions
        await self._cleanup_expired_sessions()
        
        # Check for available sessions
        for session in self.active_sessions:
            if (session.request_count < self.config.max_requests_per_session and
                time.time() - session.created_at < self.config.session_duration):
                return session
        
        # Create new session if under limit
        if len(self.active_sessions) < self.max_concurrent_sessions:
            return await self._create_new_session()
        
        # Reuse least recently used session
        if self.active_sessions:
            return min(self.active_sessions, key=lambda s: s.last_used)
        
        return None
    
    async def _create_new_session(self) -> Optional[ProxySession]:
        """Create a new proxy session."""
        try:
            session_id = self._generate_session_id()
            proxy_url = self._build_proxy_url(session_id)
            
            # Test the proxy before adding it
            if await self._test_proxy(proxy_url):
                session = ProxySession(
                    proxy_url=proxy_url,
                    created_at=time.time()
                )
                self.active_sessions.append(session)
                logger.info(f"Created new proxy session: {proxy_url[:50]}...")
                return session
            else:
                logger.warning(f"Proxy test failed for: {proxy_url[:50]}...")
                return None
                
        except Exception as e:
            logger.error(f"Failed to create proxy session: {e}")
            return None
    
    async def _test_proxy(self, proxy_url: str) -> bool:
        """Test if a proxy is working."""
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            
            # Try different approaches for SOCKS5
            try:
                from aiohttp_socks import ProxyConnector
                connector = ProxyConnector.from_url(proxy_url)
            except ImportError:
                try:
                    connector = aiohttp.ProxyConnector.from_url(proxy_url)
                except AttributeError:
                    logger.warning("SOCKS5 support not available")
                    return False
            
            async with aiohttp.ClientSession(
                timeout=timeout,
                connector=connector
            ) as session:
                # Test with a simple request
                async with session.get('http://httpbin.org/ip', timeout=5) as response:
                    if response.status == 200:
                        return True
            return False
        except Exception as e:
            logger.debug(f"Proxy test failed: {e}")
            return False
    
    async def _cleanup_expired_sessions(self):
        """Remove expired proxy sessions."""
        current_time = time.time()
        expired_sessions = [
            session for session in self.active_sessions
            if (current_time - session.created_at > self.config.session_duration or
                session.request_count >= self.config.max_requests_per_session)
        ]
        
        for session in expired_sessions:
            self.active_sessions.remove(session)
            logger.debug(f"Removed expired proxy session: {session.proxy_url[:50]}...")
    
    def mark_proxy_failed(self, proxy_url: str):
        """Mark a proxy as failed (temporarily blacklist it)."""
        self.failed_proxies[proxy_url] = time.time()
        logger.warning(f"Marked proxy as failed: {proxy_url[:50]}...")
    
    def is_proxy_blacklisted(self, proxy_url: str) -> bool:
        """Check if a proxy is currently blacklisted."""
        if proxy_url in self.failed_proxies:
            if time.time() - self.failed_proxies[proxy_url] > self.proxy_blacklist_duration:
                del self.failed_proxies[proxy_url]
                return False
            return True
        return False
    
    def update_session_stats(self, session: ProxySession, success: bool):
        """Update session statistics."""
        session.request_count += 1
        session.last_used = time.time()
        
        if success:
            session.success_count += 1
        else:
            session.failure_count += 1
    
    async def get_proxy_connector(self) -> Optional[aiohttp.BaseConnector]:
        """Get a proxy connector for aiohttp."""
        session = await self.get_proxy_session()
        if session:
            try:
                from aiohttp_socks import ProxyConnector
                return ProxyConnector.from_url(session.proxy_url)
            except ImportError:
                # Fallback to regular aiohttp if aiohttp-socks is not available
                try:
                    return aiohttp.ProxyConnector.from_url(session.proxy_url)
                except AttributeError:
                    logger.warning("SOCKS5 support not available. Install aiohttp-socks for Tor support.")
                    return None
        return None
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get statistics about proxy usage."""
        total_sessions = len(self.active_sessions)
        total_requests = sum(s.request_count for s in self.active_sessions)
        total_success = sum(s.success_count for s in self.active_sessions)
        total_failures = sum(s.failure_count for s in self.active_sessions)
        
        return {
            'active_sessions': total_sessions,
            'total_requests': total_requests,
            'success_rate': total_success / max(total_requests, 1),
            'blacklisted_proxies': len(self.failed_proxies),
            'provider': self.config.provider.value
        }

class TorProxyManager(ProxyManager):
    """Specialized proxy manager for Tor network with enhanced functionality."""
    
    def __init__(self, host: str = '127.0.0.1', port: int = 9050, control_port: int = 9051, 
                 control_password: Optional[str] = None):
        # Tor typically runs on localhost:9050 for SOCKS5
        config = ProxyConfig(
            provider=ProxyProvider.TOR,
            host=host,
            port=port
        )
        super().__init__(config)
        self.control_port = control_port
        self.control_password = control_password
        self.circuit_count = 0
        self.max_circuits = 10
        
    def _build_proxy_url(self, session_id: Optional[str] = None) -> str:
        """Build Tor SOCKS5 proxy URL."""
        return f"socks5://{self.config.host}:{self.config.port}"
    
    async def _test_proxy(self, proxy_url: str) -> bool:
        """Test Tor proxy connectivity."""
        try:
            # Test if Tor is running and accessible
            timeout = aiohttp.ClientTimeout(total=10)
            
            # Try different approaches for SOCKS5
            try:
                from aiohttp_socks import ProxyConnector
                connector = ProxyConnector.from_url(proxy_url)
            except ImportError:
                try:
                    connector = aiohttp.ProxyConnector.from_url(proxy_url)
                except AttributeError:
                    logger.warning("SOCKS5 support not available")
                    return False
            
            async with aiohttp.ClientSession(
                timeout=timeout,
                connector=connector
            ) as session:
                # Test with a simple request
                async with session.get('http://httpbin.org/ip', timeout=10) as response:
                    if response.status == 200:
                        return True
            return False
        except Exception as e:
            logger.debug(f"Tor proxy test failed: {e}")
            return False
    
    async def renew_tor_identity(self) -> bool:
        """Renew Tor identity to get a new IP address."""
        try:
            if not self.control_password:
                logger.warning("Tor control password not set, cannot renew identity")
                return False
            
            # Connect to Tor control port
            reader, writer = await asyncio.open_connection(
                self.config.host, self.control_port
            )
            
            # Authenticate
            auth_command = f'AUTHENTICATE "{self.control_password}"\r\n'
            writer.write(auth_command.encode())
            await writer.drain()
            
            response = await reader.read(1024)
            if b'250 OK' not in response:
                logger.error(f"Tor authentication failed: {response}")
                return False
            
            # Signal new identity
            signal_command = b'SIGNAL NEWNYM\r\n'
            writer.write(signal_command)
            await writer.drain()
            
            response = await reader.read(1024)
            if b'250 OK' in response:
                logger.info("Successfully renewed Tor identity")
                self.circuit_count += 1
                writer.close()
                await writer.wait_closed()
                return True
            else:
                logger.error(f"Failed to renew Tor identity: {response}")
                return False
                
        except Exception as e:
            logger.error(f"Error renewing Tor identity: {e}")
            return False
    
    async def get_tor_ip(self) -> Optional[str]:
        """Get current Tor IP address."""
        try:
            session = await self.get_proxy_session()
            if not session:
                return None
            
            timeout = aiohttp.ClientTimeout(total=10)
            connector = await self.get_proxy_connector()
            if not connector:
                return None
            
            async with aiohttp.ClientSession(
                timeout=timeout,
                connector=connector
            ) as session:
                async with session.get('http://httpbin.org/ip', timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('origin', '').split(',')[0].strip()
            return None
        except Exception as e:
            logger.error(f"Error getting Tor IP: {e}")
            return None
    
    async def _create_new_session(self) -> Optional[ProxySession]:
        """Create a new Tor session with optional identity renewal."""
        # Renew identity if we've used too many circuits
        if self.circuit_count >= self.max_circuits:
            await self.renew_tor_identity()
            self.circuit_count = 0
        
        return await super()._create_new_session()
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get enhanced statistics for Tor usage."""
        stats = super().get_session_stats()
        stats.update({
            'circuit_count': self.circuit_count,
            'max_circuits': self.max_circuits,
            'control_port': self.control_port,
            'control_enabled': self.control_password is not None
        })
        return stats

async def create_proxy_manager_from_env() -> Optional[ProxyManager]:
    """Create proxy manager from environment variables."""
    provider_name = os.getenv('PROXY_PROVIDER')
    if not provider_name:
        return None
    
    try:
        provider = ProxyProvider(provider_name.lower())
    except ValueError:
        logger.error(f"Unknown proxy provider: {provider_name}")
        return None
    
    config = ProxyConfig(
        provider=provider,
        username=os.getenv('PROXY_USERNAME'),
        password=os.getenv('PROXY_PASSWORD'),
        host=os.getenv('PROXY_HOST'),
        port=int(os.getenv('PROXY_PORT', '0')) or None,
        country=os.getenv('PROXY_COUNTRY'),
        city=os.getenv('PROXY_CITY'),
        session_duration=int(os.getenv('PROXY_SESSION_DURATION', '600')),
        max_requests_per_session=int(os.getenv('PROXY_MAX_REQUESTS', '100')),
        retry_attempts=int(os.getenv('PROXY_RETRY_ATTEMPTS', '3')),
        timeout=int(os.getenv('PROXY_TIMEOUT', '30'))
    )
    
    if provider == ProxyProvider.TOR:
        # Initialize Tor service if not already running
        from utils.tor_service import get_tor_service, initialize_tor_service
        
        tor_service = get_tor_service()
        if not tor_service:
            tor_service = await initialize_tor_service()
            if not tor_service:
                logger.error("❌ Failed to initialize Tor service")
                return None
        
        # Ensure Tor is running
        if not await tor_service.health_check():
            logger.error("❌ Tor service is not healthy")
            return None
        
        return TorProxyManager(
            host=os.getenv('TOR_HOST', '127.0.0.1'),
            port=int(os.getenv('TOR_PORT', '9050')),
            control_port=int(os.getenv('TOR_CONTROL_PORT', '9051')),
            control_password=os.getenv('TOR_CONTROL_PASSWORD')
        )
    else:
        return ProxyManager(config) 