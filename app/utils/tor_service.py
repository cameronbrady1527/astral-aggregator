# ==============================================================================
# tor_service.py — Tor Service Management
# ==============================================================================
# Purpose: Automatically manage Tor service startup and configuration
# ==============================================================================

import asyncio
import subprocess
import platform
import logging
import os
import signal
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class TorConfig:
    """Tor configuration settings."""
    socks_port: int = 9050
    control_port: int = 9051
    data_directory: Optional[Path] = None
    log_file: Optional[Path] = None
    tor_browser_path: Optional[Path] = None
    auto_start: bool = True
    auto_restart: bool = True
    max_restart_attempts: int = 3

class TorServiceManager:
    """Manages Tor service lifecycle and configuration."""
    
    def __init__(self, config: TorConfig):
        self.config = config
        self.process: Optional[subprocess.Popen] = None
        self.restart_count = 0
        self.is_running = False
        self._setup_directories()
        self._find_tor_executable()
    
    def _setup_directories(self):
        """Setup Tor data and log directories."""
        if not self.config.data_directory:
            if platform.system().lower() == "windows":
                self.config.data_directory = Path.home() / "AppData" / "Roaming" / "tor"
            else:
                self.config.data_directory = Path.home() / ".tor"
        
        if not self.config.log_file:
            self.config.log_file = self.config.data_directory / "tor.log"
        
        # Create directories
        self.config.data_directory.mkdir(parents=True, exist_ok=True)
        self.config.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def _find_tor_executable(self):
        """Find Tor executable on the system."""
        # Check for standalone tor command
        try:
            result = subprocess.run(
                ["tor", "--version"], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            if result.returncode == 0:
                self.config.tor_browser_path = Path("tor")
                logger.info(f"Found standalone Tor: {result.stdout.strip()}")
                return
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        # Check for Tor Browser's tor daemon
        tor_browser_paths = [
            Path.home() / "OneDrive" / "Desktop" / "Tor Browser" / "Browser" / "TorBrowser" / "Tor" / "tor.exe",
            Path.home() / "Desktop" / "Tor Browser" / "Browser" / "TorBrowser" / "Tor" / "tor.exe",
            Path.home() / "Downloads" / "Tor Browser" / "Browser" / "TorBrowser" / "Tor" / "tor.exe",
            Path.home() / "AppData" / "Local" / "Tor Browser" / "Browser" / "TorBrowser" / "Tor" / "tor.exe",
        ]
        
        for tor_path in tor_browser_paths:
            if tor_path.exists():
                self.config.tor_browser_path = tor_path
                logger.info(f"Found Tor Browser's Tor daemon: {tor_path}")
                return
        
        logger.warning("❌ Tor executable not found")
        logger.info("💡 Please install Tor or Tor Browser")
    
    def _create_torrc(self) -> Path:
        """Create Tor configuration file."""
        torrc_path = self.config.data_directory / "torrc"
        
        torrc_content = f"""# Tor configuration for Aggregator
# Generated automatically

# SOCKS5 proxy settings
SocksPort {self.config.socks_port}

# Logging
Log notice file {self.config.log_file}

# Circuit settings
MaxCircuitDirtiness 600
NewCircuitPeriod 150

# Connection settings
ConnectionPadding 1
ReducedConnectionPadding 0

# DNS settings
DNSPort 0
AutomapHostsOnResolve 1

# Performance settings
NumEntryGuards 6
KeepalivePeriod 300
"""
        
        with open(torrc_path, 'w') as f:
            f.write(torrc_content)
        
        logger.info(f"Created Tor configuration: {torrc_path}")
        return torrc_path
    
    def _is_tor_running(self) -> bool:
        """Check if Tor is running on the configured port."""
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('127.0.0.1', self.config.socks_port))
            sock.close()
            return result == 0
        except:
            return False
    
    async def start(self) -> bool:
        """Start Tor service."""
        if not self.config.tor_browser_path:
            logger.error("❌ Tor executable not found")
            return False
        
        if self._is_tor_running():
            logger.info("✅ Tor is already running")
            self.is_running = True
            return True
        
        try:
            # Create configuration
            torrc_path = self._create_torrc()
            
            # Start Tor process
            cmd = [str(self.config.tor_browser_path), "-f", str(torrc_path)]
            
            logger.info(f"Starting Tor: {' '.join(cmd)}")
            
            # Start process
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for Tor to start
            await self._wait_for_startup()
            
            if self._is_tor_running():
                logger.info("✅ Tor started successfully")
                self.is_running = True
                return True
            else:
                logger.error("❌ Tor failed to start")
                await self.stop()
                return False
                
        except Exception as e:
            logger.error(f"❌ Error starting Tor: {e}")
            return False
    
    async def _wait_for_startup(self, timeout: int = 30):
        """Wait for Tor to start up."""
        logger.info("⏳ Waiting for Tor to initialize...")
        
        start_time = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start_time < timeout:
            if self._is_tor_running():
                return True
            
            # Check if process is still running
            if self.process and self.process.poll() is not None:
                # Process died
                stdout, stderr = self.process.communicate()
                logger.error(f"Tor process died: {stderr}")
                return False
            
            await asyncio.sleep(1)
        
        logger.error("❌ Tor startup timeout")
        return False
    
    async def stop(self):
        """Stop Tor service."""
        if self.process:
            logger.info("Stopping Tor...")
            
            # Send SIGTERM
            try:
                self.process.terminate()
                # Use asyncio.to_thread to run the blocking wait() in a thread
                await asyncio.wait_for(asyncio.to_thread(self.process.wait), timeout=10)
            except asyncio.TimeoutError:
                # Force kill if it doesn't terminate
                logger.warning("Force killing Tor process")
                self.process.kill()
                await asyncio.to_thread(self.process.wait)
            
            self.process = None
        
        self.is_running = False
        logger.info("✅ Tor stopped")
    
    async def restart(self) -> bool:
        """Restart Tor service."""
        if self.restart_count >= self.config.max_restart_attempts:
            logger.error("❌ Max restart attempts reached")
            return False
        
        logger.info(f"Restarting Tor (attempt {self.restart_count + 1})")
        await self.stop()
        self.restart_count += 1
        
        success = await self.start()
        if success:
            self.restart_count = 0
        
        return success
    
    def get_status(self) -> Dict[str, Any]:
        """Get Tor service status."""
        return {
            'running': self.is_running,
            'port': self.config.socks_port,
            'process_id': self.process.pid if self.process else None,
            'restart_count': self.restart_count,
            'config_file': str(self.config.data_directory / "torrc"),
            'log_file': str(self.config.log_file)
        }
    
    async def health_check(self) -> bool:
        """Check if Tor is healthy."""
        if not self._is_tor_running():
            if self.config.auto_restart:
                logger.warning("Tor not running, attempting restart")
                return await self.restart()
            return False
        return True

# Global Tor service instance
_tor_service: Optional[TorServiceManager] = None

def get_tor_service() -> Optional[TorServiceManager]:
    """Get the global Tor service instance."""
    return _tor_service

async def initialize_tor_service(config: Optional[TorConfig] = None) -> Optional[TorServiceManager]:
    """Initialize the global Tor service."""
    global _tor_service
    
    if config is None:
        config = TorConfig()
    
    _tor_service = TorServiceManager(config)
    
    if config.auto_start:
        success = await _tor_service.start()
        if not success:
            logger.error("❌ Failed to start Tor service")
            return None
    
    return _tor_service

async def shutdown_tor_service():
    """Shutdown the global Tor service."""
    global _tor_service
    
    if _tor_service:
        await _tor_service.stop()
        _tor_service = None 