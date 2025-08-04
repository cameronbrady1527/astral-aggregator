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

def get_config_manager() -> ConfigManager:
    """Get the configuration manager instance."""
    config_file = os.environ.get('CONFIG_FILE', "config/sites.yaml")
    return ConfigManager(config_file)

def get_baseline_manager() -> BaselineManager:
    """Get the baseline manager instance."""
    baseline_dir = os.environ.get('BASELINE_DIR', "baselines")
    return BaselineManager(baseline_dir)

def get_baseline_merger() -> BaselineMerger:
    """Get the baseline merger instance."""
    return BaselineMerger()

def get_change_detector() -> ChangeDetector:
    """Get the change detector instance with baseline evolution enabled."""
    config_file = os.environ.get('CONFIG_FILE', "config/sites.yaml")
    return ChangeDetector(config_file)

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