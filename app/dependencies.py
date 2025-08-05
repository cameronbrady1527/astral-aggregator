# ==============================================================================
# dependencies.py — Dependency Injection Configuration
# ==============================================================================
# Purpose: Centralized dependency injection for the change detection system
# Sections: Imports, Dependency Functions
# ==============================================================================

# ==============================================================================
# Imports
# ==============================================================================

# Standard Library -----
import os
from typing import Optional

# Internal -----
from .utils.config import ConfigManager
from .utils.baseline_manager import BaselineManager
from .utils.baseline_merger import BaselineMerger
from .crawler.change_detector import ChangeDetector

# ==============================================================================
# Dependency Functions
# ==============================================================================

# Global instances for singleton pattern
_config_manager = None
_baseline_manager = None
_change_detector = None

def get_config_manager() -> ConfigManager:
    """Get the configuration manager instance (singleton)."""
    global _config_manager
    if _config_manager is None:
        config_file = os.environ.get('CONFIG_FILE', "config/sites.yaml")
        _config_manager = ConfigManager(config_file)
    return _config_manager

def get_baseline_manager() -> BaselineManager:
    """Get the baseline manager instance (singleton)."""
    global _baseline_manager
    if _baseline_manager is None:
        baseline_dir = os.environ.get('BASELINE_DIR', "baselines")
        _baseline_manager = BaselineManager(baseline_dir)
    return _baseline_manager

def get_baseline_merger() -> BaselineMerger:
    """Get the baseline merger instance."""
    return BaselineMerger()

def get_change_detector() -> ChangeDetector:
    """Get the change detector instance with baseline evolution enabled (singleton)."""
    global _change_detector
    if _change_detector is None:
        config_file = os.environ.get('CONFIG_FILE', "config/sites.yaml")
        _change_detector = ChangeDetector(config_file)
    return _change_detector

def get_change_detector_with_baseline_manager() -> tuple[ChangeDetector, BaselineManager]:
    """Get both change detector and baseline manager instances."""
    change_detector = get_change_detector()
    baseline_manager = get_baseline_manager()
    return change_detector, baseline_manager

# ==============================================================================
# Configuration Helpers
# ==============================================================================

def is_baseline_evolution_enabled() -> bool:
    """Check if baseline evolution is enabled."""
    return os.environ.get('BASELINE_EVOLUTION_ENABLED', 'true').lower() == 'true'

def get_baseline_retention_days() -> int:
    """Get the number of days to retain old baselines."""
    return int(os.environ.get('BASELINE_RETENTION_DAYS', '30'))

def get_baseline_auto_cleanup() -> bool:
    """Check if automatic baseline cleanup is enabled."""
    return os.environ.get('BASELINE_AUTO_CLEANUP', 'true').lower() == 'true' 