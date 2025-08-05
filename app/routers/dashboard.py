# ==============================================================================
# dashboard.py — Dashboard Router for Website Change Detection
# ==============================================================================
# Purpose: Provide dashboard endpoints and HTML templates
# Sections: Imports, Router Configuration, Dashboard Endpoints
# ==============================================================================

# ==============================================================================
# Imports
# ==============================================================================

# Standard Library -----
from typing import Dict, Any
import time

# Third-Party -----
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

# ==============================================================================
# Router Configuration
# ==============================================================================

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/simplified")
async def simplified_dashboard():
    """Dashboard endpoint for simplified change detection system."""
    try:
        from ..utils.simplified_change_detector import SimplifiedChangeDetector
        from pathlib import Path
        import json
        
        detector = SimplifiedChangeDetector()
        baseline_manager = detector.baseline_manager
        
        # Get baseline events
        baseline_events = baseline_manager.get_baseline_events(limit=10)
        
        # Get changes directory info
        changes_dir = Path("changes")
        change_files = []
        if changes_dir.exists():
            change_files = list(changes_dir.glob("*_changes.json"))
            change_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        # Get recent changes summary
        recent_changes = []
        for file_path in change_files[:5]:  # Last 5 change files
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    recent_changes.append({
                        "file": file_path.name,
                        "site_name": data.get("metadata", {}).get("site_name", "Unknown"),
                        "total_changes": data.get("metadata", {}).get("total_changes", 0),
                        "detection_time": data.get("metadata", {}).get("detection_time", ""),
                        "file_created": data.get("metadata", {}).get("file_created", "")
                    })
            except Exception as e:
                print(f"Error reading change file {file_path}: {e}")
        
        return {
            "status": "success",
            "simplified_system": {
                "available": True,
                "baseline_events": baseline_events,
                "total_change_files": len(change_files),
                "recent_changes": recent_changes,
                "changes_directory": str(changes_dir.absolute()) if changes_dir.exists() else None
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "simplified_system": {
                "available": False,
                "error": str(e)
            }
        }

# ==============================================================================
# Dashboard Endpoints
# ==============================================================================

@router.get("/", response_class=HTMLResponse)
async def dashboard():
    """Main dashboard for viewing change detection results."""
    
    # Get simplified system status
    simplified_status = {}
    try:
        from ..utils.simplified_change_detector import SimplifiedChangeDetector
        detector = SimplifiedChangeDetector()
        baseline_manager = detector.baseline_manager
        
        # Get recent baseline events
        baseline_events = baseline_manager.get_baseline_events(limit=5)
        
        # Get changes directory info
        from pathlib import Path
        changes_dir = Path("changes")
        if changes_dir.exists():
            change_files = list(changes_dir.glob("*_changes.json"))
            simplified_status = {
                "available": True,
                "baseline_events": baseline_events,
                "total_change_files": len(change_files),
                "recent_changes": len([f for f in change_files if f.stat().st_mtime > (time.time() - 86400)])  # Last 24 hours
            }
        else:
            simplified_status = {
                "available": True,
                "baseline_events": baseline_events,
                "total_change_files": 0,
                "recent_changes": 0
            }
    except Exception as e:
        simplified_status = {
            "available": False,
            "error": str(e)
        }
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Astral - Website Change Detection Dashboard</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/date-fns@2.29.3/index.min.js"></script>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
                min-height: 100vh;
                color: #e2e8f0;
                line-height: 1.6;
            }
            
            .container {
                max-width: 1600px;
                margin: 0 auto;
                padding: 20px;
            }
            
            .header {
                text-align: center;
                margin-bottom: 40px;
                color: white;
            }
            
            .header h1 {
                font-size: 3.5rem;
                margin-bottom: 10px;
                text-shadow: 0 4px 8px rgba(0,0,0,0.3);
                font-weight: 700;
                background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .header p {
                font-size: 1.3rem;
                opacity: 0.9;
                font-weight: 400;
                color: #94a3b8;
            }
            
            .status-bar {
                background: rgba(30, 41, 59, 0.8);
                backdrop-filter: blur(20px);
                border: 1px solid rgba(148, 163, 184, 0.2);
                border-radius: 16px;
                padding: 24px;
                margin-bottom: 30px;
                color: white;
                display: flex;
                justify-content: space-between;
                align-items: center;
                flex-wrap: wrap;
                gap: 20px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            }
            
            .status-item {
                text-align: center;
            }
            
            .status-number {
                font-size: 2.2rem;
                font-weight: 700;
                display: block;
                background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .status-label {
                font-size: 0.9rem;
                opacity: 0.8;
                text-transform: uppercase;
                letter-spacing: 1px;
                color: #94a3b8;
                font-weight: 500;
            }
            
            .dashboard-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
                gap: 25px;
                margin-bottom: 30px;
            }
            
            .card {
                background: rgba(30, 41, 59, 0.8);
                backdrop-filter: blur(20px);
                border: 1px solid rgba(148, 163, 184, 0.2);
                border-radius: 16px;
                padding: 30px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                transition: all 0.3s ease;
            }
            
            .card:hover {
                transform: translateY(-4px);
                box-shadow: 0 16px 48px rgba(0, 0, 0, 0.4);
                border-color: rgba(96, 165, 250, 0.3);
            }
            
            .card h3 {
                color: #60a5fa;
                margin-bottom: 20px;
                font-size: 1.4rem;
                font-weight: 600;
                display: flex;
                align-items: center;
                gap: 12px;
            }
            
            .card-icon {
                font-size: 1.6rem;
                opacity: 0.9;
            }
            
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 20px;
                margin-bottom: 25px;
            }
            
            .stat {
                text-align: center;
                padding: 20px;
                background: rgba(51, 65, 85, 0.6);
                border: 1px solid rgba(148, 163, 184, 0.2);
                border-radius: 12px;
                border-left: 4px solid #60a5fa;
                transition: transform 0.2s ease;
            }
            
            .stat:hover {
                transform: scale(1.02);
                background: rgba(51, 65, 85, 0.8);
            }
            
            .stat-number {
                font-size: 2.2rem;
                font-weight: 700;
                color: #60a5fa;
                margin-bottom: 5px;
            }
            
            .stat-label {
                font-size: 0.9rem;
                color: #94a3b8;
                font-weight: 500;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .actions {
                display: flex;
                gap: 12px;
                flex-wrap: wrap;
            }
            
            .btn {
                padding: 14px 24px;
                border: none;
                border-radius: 12px;
                cursor: pointer;
                font-weight: 600;
                text-decoration: none;
                display: inline-flex;
                align-items: center;
                gap: 8px;
                transition: all 0.3s ease;
                font-size: 0.95rem;
                min-width: 140px;
                justify-content: center;
                backdrop-filter: blur(10px);
            }
            
            .btn-primary {
                background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
                color: white;
                box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
                border: 1px solid rgba(59, 130, 246, 0.2);
            }
            
            .btn-primary:hover {
                background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4);
            }
            
            .btn-secondary {
                background: rgba(71, 85, 105, 0.8);
                color: #e2e8f0;
                border: 1px solid rgba(148, 163, 184, 0.3);
            }
            
            .btn-secondary:hover {
                background: rgba(71, 85, 105, 1);
                transform: translateY(-2px);
                border-color: rgba(148, 163, 184, 0.5);
            }
            
            .btn-success {
                background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                color: white;
                box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
                border: 1px solid rgba(16, 185, 129, 0.2);
            }
            
            .btn-success:hover {
                background: linear-gradient(135deg, #059669 0%, #047857 100%);
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(16, 185, 129, 0.4);
            }
            
            .btn-warning {
                background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
                color: white;
                box-shadow: 0 4px 15px rgba(245, 158, 11, 0.3);
                border: 1px solid rgba(245, 158, 11, 0.2);
            }
            
            .btn-warning:hover {
                background: linear-gradient(135deg, #d97706 0%, #b45309 100%);
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(245, 158, 11, 0.4);
            }
            
            .site-list {
                margin-top: 20px;
            }
            
            .site-item {
                background: rgba(51, 65, 85, 0.6);
                border: 1px solid rgba(148, 163, 184, 0.2);
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 15px;
                border-left: 4px solid #60a5fa;
                transition: all 0.3s ease;
            }
            
            .site-item:hover {
                background: rgba(51, 65, 85, 0.8);
                transform: translateX(5px);
                border-color: rgba(96, 165, 250, 0.4);
            }
            
            .site-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 10px;
            }
            
            .site-name {
                font-weight: 600;
                color: #e2e8f0;
                font-size: 1.1rem;
            }
            
            .site-status {
                padding: 6px 16px;
                border-radius: 20px;
                font-size: 0.8rem;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .status-active {
                background: rgba(16, 185, 129, 0.2);
                color: #10b981;
                border: 1px solid rgba(16, 185, 129, 0.3);
            }
            
            .status-inactive {
                background: rgba(239, 68, 68, 0.2);
                color: #ef4444;
                border: 1px solid rgba(239, 68, 68, 0.3);
            }
            
            .site-details {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
                gap: 15px;
                font-size: 0.9rem;
            }
            
            .detail-item {
                text-align: center;
            }
            
            .detail-value {
                font-weight: 600;
                color: #60a5fa;
                font-size: 1.1rem;
            }
            
            .detail-label {
                color: #94a3b8;
                font-size: 0.8rem;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .chart-container {
                position: relative;
                height: 300px;
                margin-top: 20px;
            }
            
            .recent-changes {
                max-height: 400px;
                overflow-y: auto;
            }
            
            .change-item {
                background: rgba(51, 65, 85, 0.6);
                border: 1px solid rgba(148, 163, 184, 0.2);
                border-radius: 12px;
                padding: 15px;
                margin-bottom: 10px;
                border-left: 4px solid #10b981;
                transition: all 0.3s ease;
            }
            
            .change-item:hover {
                background: rgba(51, 65, 85, 0.8);
                transform: translateX(5px);
            }
            
            .change-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 8px;
            }
            
            .change-site {
                font-weight: 600;
                color: #e2e8f0;
            }
            
            .change-time {
                font-size: 0.8rem;
                color: #94a3b8;
            }
            
            .change-summary {
                font-size: 0.9rem;
                color: #94a3b8;
            }
            
            .loading {
                text-align: center;
                padding: 40px;
                color: #94a3b8;
            }
            
            .spinner {
                border: 4px solid rgba(148, 163, 184, 0.2);
                border-top: 4px solid #60a5fa;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 0 auto 20px;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            .error {
                background: rgba(239, 68, 68, 0.1);
                color: #ef4444;
                padding: 15px;
                border-radius: 12px;
                margin: 20px 0;
                border-left: 4px solid #ef4444;
                border: 1px solid rgba(239, 68, 68, 0.3);
            }
            
            .success {
                background: rgba(16, 185, 129, 0.1);
                color: #10b981;
                padding: 15px;
                border-radius: 12px;
                margin: 20px 0;
                border-left: 4px solid #10b981;
                border: 1px solid rgba(16, 185, 129, 0.3);
            }
            
            .tabs {
                display: flex;
                margin-bottom: 20px;
                border-bottom: 2px solid rgba(148, 163, 184, 0.2);
            }
            
            .tab {
                padding: 12px 24px;
                cursor: pointer;
                border-bottom: 2px solid transparent;
                transition: all 0.3s ease;
                font-weight: 600;
                color: #94a3b8;
            }
            
            .tab.active {
                border-bottom-color: #60a5fa;
                color: #60a5fa;
            }
            
            .tab:hover {
                background: rgba(51, 65, 85, 0.3);
                color: #e2e8f0;
            }
            
            .tab-content {
                display: none;
            }
            
            .tab-content.active {
                display: block;
            }
            
            .refresh-indicator {
                position: fixed;
                top: 20px;
                right: 20px;
                background: rgba(30, 41, 59, 0.9);
                backdrop-filter: blur(20px);
                border: 1px solid rgba(148, 163, 184, 0.2);
                padding: 12px 18px;
                border-radius: 12px;
                font-size: 0.9rem;
                color: #60a5fa;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                z-index: 1000;
                display: none;
            }
            
            .baseline-event {
                background: rgba(51, 65, 85, 0.6);
                border: 1px solid rgba(148, 163, 184, 0.2);
                border-radius: 12px;
                padding: 15px;
                margin-bottom: 10px;
                transition: all 0.3s ease;
            }
            
            .baseline-event:hover {
                background: rgba(51, 65, 85, 0.8);
                transform: translateX(5px);
            }
            
            .baseline-event.created {
                border-left: 4px solid #10b981;
            }
            
            .baseline-event.updated {
                border-left: 4px solid #f59e0b;
            }
            
            .baseline-event.error {
                border-left: 4px solid #ef4444;
            }
            
            .baseline-event.validation {
                border-left: 4px solid #60a5fa;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🌌 Astral</h1>
                <p>AI-Driven Infrastructure for Operational Intelligence</p>
                <p style="font-size: 1rem; margin-top: 10px; color: #60a5fa;">✨ Using Simplified Change Detection System</p>
            </div>
            
            <div class="refresh-indicator" id="refreshIndicator">
                🔄 Auto-refreshing every 30 seconds
            </div>
            
            <div class="status-bar" id="statusBar">
                <div class="status-item">
                    <span class="status-number" id="totalSites">-</span>
                    <span class="status-label">Sites</span>
                </div>
                <div class="status-item">
                    <span class="status-number" id="totalUrls">-</span>
                    <span class="status-label">URLs Monitored</span>
                </div>
                <div class="status-item">
                    <span class="status-number" id="totalChanges">-</span>
                    <span class="status-label">Changes Detected</span>
                </div>
                <div class="status-item">
                    <span class="status-number" id="totalBaselines">-</span>
                    <span class="status-label">Active Baselines</span>
                </div>
                <div class="status-item">
                    <span class="status-number" id="lastUpdate">-</span>
                    <span class="status-label">Last Update</span>
                </div>
            </div>
            
            <div class="dashboard-grid">
                <!-- Real-time Monitoring -->
                <div class="card">
                    <h3><span class="card-icon">📡</span> Real-time Monitoring</h3>
                    <div id="realtimeContent">
                        <div class="loading">
                            <div class="spinner"></div>
                            Loading real-time data...
                        </div>
                    </div>
                </div>
                
                <!-- System Analytics -->
                <div class="card">
                    <h3><span class="card-icon">📊</span> System Analytics</h3>
                    <div id="analyticsContent">
                        <div class="loading">
                            <div class="spinner"></div>
                            Loading analytics...
                        </div>
                    </div>
                </div>
                
                <!-- Recent Changes -->
                <div class="card">
                    <h3><span class="card-icon">🔄</span> Recent Changes</h3>
                    <div id="recentChangesContent">
                        <div class="loading">
                            <div class="spinner"></div>
                            Loading recent changes...
                        </div>
                    </div>
                </div>
                
                <!-- Historical Trends -->
                <div class="card">
                    <h3><span class="card-icon">📈</span> Historical Trends</h3>
                    <div class="tabs">
                        <div class="tab active" onclick="switchTab('urls')">URL Growth</div>
                        <div class="tab" onclick="switchTab('changes')">Change Activity</div>
                    </div>
                    <div id="urlsTab" class="tab-content active">
                        <div class="chart-container">
                            <canvas id="urlsChart"></canvas>
                        </div>
                    </div>
                    <div id="changesTab" class="tab-content">
                        <div class="chart-container">
                            <canvas id="changesChart"></canvas>
                        </div>
                    </div>
                </div>
                
                <!-- Site Management -->
                <div class="card">
                    <h3><span class="card-icon">⚙️</span> Site Management</h3>
                    <div class="actions">
                        <button class="btn btn-success" onclick="triggerAllSites()">
                            🚀 Simplified Trigger All Sites
                        </button>
                        <button class="btn btn-primary" onclick="refreshData()">
                            🔄 Refresh Data
                        </button>
                    </div>
                    <div id="siteManagementContent">
                        <div class="loading">
                            <div class="spinner"></div>
                            Loading site data...
                        </div>
                    </div>
                </div>
                
                <!-- Baseline Events -->
                <div class="card">
                    <h3><span class="card-icon">🎯</span> Baseline Events</h3>
                    <div id="baselineEventsContent">
                        <div class="loading">
                            <div class="spinner"></div>
                            Loading baseline events...
                        </div>
                    </div>
                </div>
                
                <!-- Detailed Analytics -->
                <div class="card">
                    <h3><span class="card-icon">🔍</span> Detailed Analytics</h3>
                    <div id="detailedAnalyticsContent">
                        <div class="loading">
                            <div class="spinner"></div>
                            Loading detailed analytics...
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            let refreshInterval;
            let urlsChart, changesChart;
            
            // Initialize dashboard
            document.addEventListener('DOMContentLoaded', function() {
                loadAllData();
                startAutoRefresh();
            });
            
            function startAutoRefresh() {
                refreshInterval = setInterval(() => {
                    showRefreshIndicator();
                    loadAllData();
                }, 30000); // Refresh every 30 seconds
            }
            
            function showRefreshIndicator() {
                const indicator = document.getElementById('refreshIndicator');
                indicator.style.display = 'block';
                setTimeout(() => {
                    indicator.style.display = 'none';
                }, 3000);
            }
            
            async function loadAllData() {
                try {
                    await Promise.all([
                        loadStatusBar(),
                        loadRealtimeData(),
                        loadAnalytics(),
                        loadRecentChanges(),
                        loadSiteManagement(),
                        loadDetailedAnalytics(),
                        loadBaselineEvents(),
                        loadHistoricalData(),
                        loadDetectionProgress()
                    ]);
                } catch (error) {
                    console.error('Error loading data:', error);
                }
            }
            
            async function loadDetectionProgress() {
                try {
                    const response = await fetch('/api/listeners/progress');
                    const data = await response.json();
                    
                    const progressContainer = document.getElementById('detection-progress');
                    if (!progressContainer) {
                        // Create progress container if it doesn't exist
                        const container = document.querySelector('.container');
                        const progressDiv = document.createElement('div');
                        progressDiv.id = 'detection-progress';
                        progressDiv.style.display = 'none';
                        container.insertBefore(progressDiv, container.firstChild);
                    }
                    
                    if (data.detection_status.is_running) {
                        progressContainer.style.display = 'block';
                        progressContainer.innerHTML = `
                            <div class="card" style="background: #e3f2fd; border-left: 4px solid #2196f3; margin-bottom: 20px;">
                                <div style="display: flex; align-items: flex-start;">
                                    <div style="margin-right: 15px;">
                                        <div class="spinner" style="width: 30px; height: 30px; border-top-color: #2196f3;"></div>
                                    </div>
                                    <div style="flex: 1;">
                                        <h3 style="color: #1976d2; font-size: 1.1rem; margin-bottom: 10px; font-weight: 600;">
                                            🔄 Detection in Progress: ${data.detection_status.current_site}
                                        </h3>
                                        <div style="color: #1565c0; font-size: 0.9rem;">
                                            <p style="margin-bottom: 10px;">${data.detection_status.message}</p>
                                            <div style="margin-top: 10px;">
                                                <div style="background: #bbdefb; border-radius: 10px; height: 8px; overflow: hidden;">
                                                    <div style="background: #2196f3; height: 100%; transition: width 0.3s ease; width: ${data.detection_status.progress}%;"></div>
                                                </div>
                                                <p style="margin-top: 5px; font-size: 0.8rem; color: #1976d2;">${data.detection_status.progress}% complete</p>
                                                ${data.detection_status.elapsed_time ? `<p style="font-size: 0.8rem; color: #1976d2; margin: 2px 0;">Elapsed: ${data.detection_status.elapsed_time}</p>` : ''}
                                                ${data.detection_status.estimated_time_remaining ? `<p style="font-size: 0.8rem; color: #1976d2; margin: 2px 0;">ETA: ${data.detection_status.estimated_time_remaining}</p>` : ''}
                                                ${data.detection_status.current_method ? `<p style="font-size: 0.8rem; color: #1976d2; margin: 2px 0;">Method: ${data.detection_status.current_method}</p>` : ''}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        `;
                    } else {
                        progressContainer.style.display = 'none';
                    }
                } catch (error) {
                    console.error('Error loading detection progress:', error);
                }
            }
            
            async function loadStatusBar() {
                try {
                    const [analyticsResponse, baselineResponse] = await Promise.all([
                        fetch('/api/listeners/analytics'),
                        fetch('/api/listeners/baseline-events?limit=1')
                    ]);
                    
                    const analyticsData = await analyticsResponse.json();
                    const baselineData = await baselineResponse.json();
                    
                    if (analyticsData.status === 'healthy') {
                        const overview = analyticsData.analytics.overview;
                        document.getElementById('totalSites').textContent = overview.total_sites;
                        document.getElementById('totalUrls').textContent = overview.total_urls_monitored.toLocaleString();
                        document.getElementById('totalChanges').textContent = overview.total_changes_detected.toLocaleString();
                        document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString();
                        
                        // Count unique sites with baselines
                        if (baselineData.status === 'success' && baselineData.baseline_events) {
                            const uniqueSites = new Set(baselineData.baseline_events.map(event => event.site_id));
                            document.getElementById('totalBaselines').textContent = uniqueSites.size;
                        } else {
                            document.getElementById('totalBaselines').textContent = '0';
                        }
                    }
                } catch (error) {
                    console.error('Error loading status bar:', error);
                }
            }
            
            async function loadRealtimeData() {
                try {
                    const response = await fetch('/api/listeners/realtime');
                    const data = await response.json();
                    
                    const content = document.getElementById('realtimeContent');
                    
                    if (data.status === 'healthy') {
                        let html = '<div class="site-list">';
                        
                        data.sites.forEach(site => {
                            const timeSince = site.time_since_last_seconds;
                            let timeDisplay = 'Unknown';
                            
                            if (timeSince !== null) {
                                if (timeSince < 60) {
                                    timeDisplay = `${Math.round(timeSince)}s ago`;
                                } else if (timeSince < 3600) {
                                    timeDisplay = `${Math.round(timeSince / 60)}m ago`;
                                } else {
                                    timeDisplay = `${Math.round(timeSince / 3600)}h ago`;
                                }
                            }
                            
                            html += `
                                <div class="site-item">
                                    <div class="site-header">
                                        <div class="site-name">${site.site_name}</div>
                                        <div class="site-status ${site.status === 'active' ? 'status-active' : 'status-inactive'}">
                                            ${site.status}
                                        </div>
                                    </div>
                                    <div class="site-details">
                                        <div class="detail-item">
                                            <div class="detail-value">${site.current_urls.toLocaleString()}</div>
                                            <div class="detail-label">URLs</div>
                                        </div>
                                        <div class="detail-item">
                                            <div class="detail-value">${site.last_change_count}</div>
                                            <div class="detail-label">Last Changes</div>
                                        </div>
                                        <div class="detail-item">
                                            <div class="detail-value">${timeDisplay}</div>
                                            <div class="detail-label">Last Detection</div>
                                        </div>
                                        <div class="detail-item">
                                            <div class="detail-value">${site.detection_methods.join(', ')}</div>
                                            <div class="detail-label">Methods</div>
                                        </div>
                                    </div>
                                </div>
                            `;
                        });
                        
                        html += '</div>';
                        content.innerHTML = html;
                    } else {
                        content.innerHTML = '<div class="error">Unable to load real-time data</div>';
                    }
                } catch (error) {
                    console.error('Error loading real-time data:', error);
                    document.getElementById('realtimeContent').innerHTML = '<div class="error">Error loading real-time data</div>';
                }
            }
            
            async function loadAnalytics() {
                try {
                    const response = await fetch('/api/listeners/analytics');
                    const data = await response.json();
                    
                    const content = document.getElementById('analyticsContent');
                    
                    if (data.status === 'healthy') {
                        const overview = data.analytics.overview;
                        const sites = data.analytics.sites;
                        
                        let html = `
                            <div class="stats-grid">
                                <div class="stat">
                                    <div class="stat-number">${overview.active_sites}</div>
                                    <div class="stat-label">Active Sites</div>
                                </div>
                                <div class="stat">
                                    <div class="stat-number">${overview.total_urls_monitored.toLocaleString()}</div>
                                    <div class="stat-label">Total URLs</div>
                                </div>
                                <div class="stat">
                                    <div class="stat-number">${overview.total_changes_detected}</div>
                                    <div class="stat-label">Total Changes</div>
                                </div>
                                <div class="stat">
                                    <div class="stat-number">${sites.length}</div>
                                    <div class="stat-label">Configured Sites</div>
                                </div>
                            </div>
                        `;
                        
                        content.innerHTML = html;
                    } else {
                        content.innerHTML = '<div class="error">Unable to load analytics</div>';
                    }
                } catch (error) {
                    console.error('Error loading analytics:', error);
                    document.getElementById('analyticsContent').innerHTML = '<div class="error">Error loading analytics</div>';
                }
            }
            
            async function loadRecentChanges() {
                try {
                    const response = await fetch('/api/listeners/changes?limit=10&use_simplified=true');
                    const data = await response.json();
                    
                    const content = document.getElementById('recentChangesContent');
                    
                    if (data.recent_changes && data.recent_changes.length > 0) {
                        let html = '<div class="recent-changes">';
                        
                        data.recent_changes.forEach(change => {
                            const time = new Date(change.detection_time).toLocaleString();
                            const summary = change.summary;
                            const changeText = summary.total_changes > 0 ? 
                                `${summary.total_changes} changes detected` : 
                                'No changes detected';
                            
                            html += `
                                <div class="change-item">
                                    <div class="change-header">
                                        <div class="change-site">${change.site_name}</div>
                                        <div class="change-time">${time}</div>
                                    </div>
                                    <div class="change-summary">${changeText}</div>
                                </div>
                            `;
                        });
                        
                        html += '</div>';
                        content.innerHTML = html;
                    } else {
                        content.innerHTML = '<div class="loading">No recent changes found</div>';
                    }
                } catch (error) {
                    console.error('Error loading recent changes:', error);
                    document.getElementById('recentChangesContent').innerHTML = '<div class="error">Error loading recent changes</div>';
                }
            }
            
            async function loadSiteManagement() {
                try {
                    const response = await fetch('/api/listeners/sites');
                    const sites = await response.json();
                    
                    const content = document.getElementById('siteManagementContent');
                    
                    if (sites && sites.length > 0) {
                        let html = '<div class="site-list">';
                        
                        sites.forEach(site => {
                            html += `
                                <div class="site-item">
                                    <div class="site-header">
                                        <div class="site-name">${site.name}</div>
                                        <div class="site-status ${site.is_active ? 'status-active' : 'status-inactive'}">
                                            ${site.is_active ? 'Active' : 'Inactive'}
                                        </div>
                                    </div>
                                    <div class="site-details">
                                        <div class="detail-item">
                                            <div class="detail-value">${site.site_id}</div>
                                            <div class="detail-label">ID</div>
                                        </div>
                                        <div class="detail-item">
                                            <div class="detail-value">${site.detection_methods.join(', ')}</div>
                                            <div class="detail-label">Methods</div>
                                        </div>
                                        <div class="detail-item">
                                            <div class="detail-value">${site.check_interval_minutes}m</div>
                                            <div class="detail-label">Interval</div>
                                        </div>
                                        <div class="detail-item">
                                            <button class="btn btn-warning" onclick="triggerSite('${site.site_id}')">
                                                Simplified Trigger
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            `;
                        });
                        
                        html += '</div>';
                        content.innerHTML = html;
                    } else {
                        content.innerHTML = '<div class="loading">No sites configured</div>';
                    }
                } catch (error) {
                    console.error('Error loading site management:', error);
                    document.getElementById('siteManagementContent').innerHTML = '<div class="error">Error loading site management</div>';
                }
            }
            
            async function loadDetailedAnalytics() {
                try {
                    const response = await fetch('/api/listeners/analytics');
                    const data = await response.json();
                    
                    const content = document.getElementById('detailedAnalyticsContent');
                    
                    if (data.status === 'healthy') {
                        const sites = data.analytics.sites;
                        
                        let html = '<div class="site-list">';
                        
                        sites.forEach(site => {
                            const lastDetection = site.last_detection ? 
                                new Date(site.last_detection).toLocaleString() : 
                                'Never';
                            
                            html += `
                                <div class="site-item">
                                    <div class="site-header">
                                        <div class="site-name">${site.site_name}</div>
                                        <div class="site-status ${site.is_active ? 'status-active' : 'status-inactive'}">
                                            ${site.is_active ? 'Active' : 'Inactive'}
                                        </div>
                                    </div>
                                    <div class="site-details">
                                        <div class="detail-item">
                                            <div class="detail-value">${site.total_urls.toLocaleString()}</div>
                                            <div class="detail-label">URLs</div>
                                        </div>
                                        <div class="detail-item">
                                            <div class="detail-value">${site.total_changes}</div>
                                            <div class="detail-label">Changes</div>
                                        </div>
                                        <div class="detail-item">
                                            <div class="detail-value">${site.new_pages}</div>
                                            <div class="detail-label">New Pages</div>
                                        </div>
                                        <div class="detail-item">
                                            <div class="detail-value">${site.modified_pages}</div>
                                            <div class="detail-label">Modified</div>
                                        </div>
                                    </div>
                                    <div style="margin-top: 10px; font-size: 0.8rem; color: #6c757d;">
                                        Last detection: ${lastDetection}
                                    </div>
                                </div>
                            `;
                        });
                        
                        html += '</div>';
                        content.innerHTML = html;
                    } else {
                        content.innerHTML = '<div class="error">Unable to load detailed analytics</div>';
                    }
                } catch (error) {
                    console.error('Error loading detailed analytics:', error);
                    document.getElementById('detailedAnalyticsContent').innerHTML = '<div class="error">Error loading detailed analytics</div>';
                }
            }
            
            async function loadBaselineEvents() {
                try {
                    const response = await fetch('/api/listeners/baseline-events?limit=10');
                    const data = await response.json();
                    
                    const content = document.getElementById('baselineEventsContent');
                    
                    if (data.status === 'success' && data.baseline_events && data.baseline_events.length > 0) {
                        let html = '<div class="recent-changes">';
                        
                        data.baseline_events.forEach(event => {
                            const time = new Date(event.timestamp).toLocaleString();
                            const details = event.details;
                            
                            let eventIcon = '🎯';
                            let eventColor = '#60a5fa';
                            let eventTitle = 'Baseline Event';
                            
                            if (event.event_type === 'baseline_created') {
                                eventIcon = '🎯';
                                eventColor = '#10b981';
                                eventTitle = 'New Baseline Created';
                            } else if (event.event_type === 'baseline_updated') {
                                eventIcon = '🔄';
                                eventColor = '#f59e0b';
                                eventTitle = 'Baseline Updated';
                            } else if (event.event_type === 'baseline_error') {
                                eventIcon = '❌';
                                eventColor = '#ef4444';
                                eventTitle = 'Baseline Error';
                            } else if (event.event_type === 'baseline_replaced') {
                                eventIcon = '🔄';
                                eventColor = '#8b5cf6';
                                eventTitle = 'Baseline Replaced';
                            } else if (event.event_type === 'baseline_validated') {
                                eventIcon = '✅';
                                eventColor = '#10b981';
                                eventTitle = 'Baseline Validated';
                            }
                            
                            let eventDetails = '';
                            if (event.event_type === 'baseline_created') {
                                eventDetails = `${details.total_urls} URLs, ${details.total_content_hashes} content hashes`;
                            } else if (event.event_type === 'baseline_updated') {
                                eventDetails = `${details.changes_applied} changes applied (${details.new_urls} new, ${details.modified_urls} modified, ${details.deleted_urls} deleted)`;
                            } else if (event.event_type === 'baseline_error') {
                                eventDetails = details.error;
                            } else if (event.event_type === 'baseline_replaced') {
                                eventDetails = `${details.total_urls} URLs, ${details.total_content_hashes} content hashes`;
                            } else if (event.event_type === 'baseline_validated') {
                                if (details.message) {
                                    eventDetails = details.message;
                                } else if (details.total_urls !== undefined) {
                                    eventDetails = `${details.total_urls} URLs validated, ${details.total_content_hashes} content hashes`;
                                } else {
                                    eventDetails = 'Baseline validation completed successfully';
                                }
                            }
                            
                            html += `
                                <div class="change-item" style="border-left-color: ${eventColor};">
                                    <div class="change-header">
                                        <div class="change-site">
                                            <span style="margin-right: 8px;">${eventIcon}</span>
                                            ${eventTitle} - ${event.site_id}
                                        </div>
                                        <div class="change-time">${time}</div>
                                    </div>
                                    <div class="change-summary">${eventDetails}</div>
                                </div>
                            `;
                        });
                        
                        html += '</div>';
                        content.innerHTML = html;
                    } else {
                        content.innerHTML = '<div class="loading">No baseline events found</div>';
                    }
                } catch (error) {
                    console.error('Error loading baseline events:', error);
                    document.getElementById('baselineEventsContent').innerHTML = '<div class="error">Error loading baseline events</div>';
                }
            }
            
            async function loadHistoricalData() {
                try {
                    const response = await fetch('/api/listeners/history?days=7');
                    const data = await response.json();
                    
                    if (data.status === 'success') {
                        createUrlsChart(data.history);
                        createChangesChart(data.history);
                    }
                } catch (error) {
                    console.error('Error loading historical data:', error);
                }
            }
            
            function createUrlsChart(historyData) {
                const ctx = document.getElementById('urlsChart').getContext('2d');
                
                if (urlsChart) {
                    urlsChart.destroy();
                }
                
                const datasets = [];
                const labels = [];
                
                // Process data for each site
                Object.keys(historyData.sites).forEach((siteId, index) => {
                    const site = historyData.sites[siteId];
                    const siteData = [];
                    
                    // Get unique dates from all detections
                    const dates = [...new Set(site.detections.map(d => d.detection_time.split('T')[0]))].sort();
                    
                    dates.forEach(date => {
                        const dayData = site.daily_summary[date];
                        if (dayData) {
                            siteData.push(dayData.total_changes);
                        } else {
                            siteData.push(0);
                        }
                    });
                    
                    if (labels.length === 0) {
                        labels.push(...dates);
                    }
                    
                    const colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe'];
                    
                    datasets.push({
                        label: site.site_name,
                        data: siteData,
                        borderColor: colors[index % colors.length],
                        backgroundColor: colors[index % colors.length] + '20',
                        tension: 0.4,
                        fill: false
                    });
                });
                
                urlsChart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: labels,
                        datasets: datasets
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                position: 'top',
                            },
                            title: {
                                display: true,
                                text: 'URL Growth Over Time'
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true
                            }
                        }
                    }
                });
            }
            
            function createChangesChart(historyData) {
                const ctx = document.getElementById('changesChart').getContext('2d');
                
                if (changesChart) {
                    changesChart.destroy();
                }
                
                const datasets = [];
                const labels = [];
                
                // Process data for each site
                Object.keys(historyData.sites).forEach((siteId, index) => {
                    const site = historyData.sites[siteId];
                    const siteData = [];
                    
                    // Get unique dates from all detections
                    const dates = [...new Set(site.detections.map(d => d.detection_time.split('T')[0]))].sort();
                    
                    dates.forEach(date => {
                        const dayData = site.daily_summary[date];
                        if (dayData) {
                            siteData.push(dayData.total_changes);
                        } else {
                            siteData.push(0);
                        }
                    });
                    
                    if (labels.length === 0) {
                        labels.push(...dates);
                    }
                    
                    const colors = ['#28a745', '#ffc107', '#dc3545', '#17a2b8', '#6f42c1'];
                    
                    datasets.push({
                        label: site.site_name,
                        data: siteData,
                        borderColor: colors[index % colors.length],
                        backgroundColor: colors[index % colors.length] + '20',
                        tension: 0.4,
                        fill: false
                    });
                });
                
                changesChart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: labels,
                        datasets: datasets
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                position: 'top',
                            },
                            title: {
                                display: true,
                                text: 'Change Activity Over Time'
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true
                            }
                        }
                    }
                });
            }
            
            function switchTab(tabName) {
                // Hide all tab contents
                document.querySelectorAll('.tab-content').forEach(content => {
                    content.classList.remove('active');
                });
                
                // Remove active class from all tabs
                document.querySelectorAll('.tab').forEach(tab => {
                    tab.classList.remove('active');
                });
                
                // Show selected tab content
                document.getElementById(tabName + 'Tab').classList.add('active');
                
                // Add active class to clicked tab
                event.target.classList.add('active');
            }
            
            async function triggerSite(siteId) {
                try {
                    const response = await fetch(`/api/listeners/trigger/${siteId}?use_simplified=true`, {
                        method: 'POST'
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        if (data.status === 'started') {
                            showSuccess(`Simplified detection started for ${siteId}. Monitoring progress...`);
                            // Start monitoring progress more frequently
                            const progressInterval = setInterval(async () => {
                                await loadDetectionProgress();
                                const progressData = await fetch('/api/listeners/progress').then(r => r.json());
                                if (!progressData.detection_status.is_running) {
                                    clearInterval(progressInterval);
                                    loadAllData();
                                }
                            }, 1000);
                        } else {
                            showSuccess(`Successfully triggered simplified detection for ${siteId}`);
                            setTimeout(() => {
                                loadAllData();
                            }, 2000);
                        }
                    } else {
                        showError(`Failed to trigger detection for ${siteId}: ${data.detail || 'Unknown error'}`);
                    }
                } catch (error) {
                    console.error('Error triggering site:', error);
                    showError(`Error triggering detection for ${siteId}`);
                }
            }
            
            async function triggerAllSites() {
                try {
                    const response = await fetch('/api/listeners/trigger/all?use_simplified=true', {
                        method: 'POST'
                    });
                    
                    if (response.ok) {
                        showSuccess('Successfully triggered simplified detection for all sites');
                        setTimeout(() => {
                            loadAllData();
                        }, 2000);
                    } else {
                        showError('Failed to trigger detection for all sites');
                    }
                } catch (error) {
                    console.error('Error triggering all sites:', error);
                    showError('Error triggering detection for all sites');
                }
            }
            
            function refreshData() {
                showRefreshIndicator();
                loadAllData();
            }
            
            function showSuccess(message) {
                const successDiv = document.createElement('div');
                successDiv.className = 'success';
                successDiv.textContent = message;
                document.querySelector('.container').insertBefore(successDiv, document.querySelector('.status-bar').nextSibling);
                
                setTimeout(() => {
                    successDiv.remove();
                }, 5000);
            }
            
            function showError(message) {
                const errorDiv = document.createElement('div');
                errorDiv.className = 'error';
                errorDiv.textContent = message;
                document.querySelector('.container').insertBefore(errorDiv, document.querySelector('.status-bar').nextSibling);
                
                setTimeout(() => {
                    errorDiv.remove();
                }, 5000);
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content) 