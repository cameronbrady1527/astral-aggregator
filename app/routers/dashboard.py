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

# Third-Party -----
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

# ==============================================================================
# Router Configuration
# ==============================================================================

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

# ==============================================================================
# Dashboard Endpoints
# ==============================================================================

@router.get("/", response_class=HTMLResponse)
async def dashboard():
    """Main dashboard for viewing change detection results."""
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
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #333;
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
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                font-weight: 300;
            }
            
            .header p {
                font-size: 1.3rem;
                opacity: 0.9;
                font-weight: 300;
            }
            
            .status-bar {
                background: rgba(255,255,255,0.1);
                backdrop-filter: blur(10px);
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 30px;
                color: white;
                display: flex;
                justify-content: space-between;
                align-items: center;
                flex-wrap: wrap;
                gap: 20px;
            }
            
            .status-item {
                text-align: center;
            }
            
            .status-number {
                font-size: 2rem;
                font-weight: 700;
                display: block;
            }
            
            .status-label {
                font-size: 0.9rem;
                opacity: 0.8;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .dashboard-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
                gap: 25px;
                margin-bottom: 30px;
            }
            
            .card {
                background: white;
                border-radius: 12px;
                padding: 30px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                transition: all 0.3s ease;
                border: 1px solid rgba(255,255,255,0.2);
            }
            
            .card:hover {
                transform: translateY(-3px);
                box-shadow: 0 12px 40px rgba(0,0,0,0.15);
            }
            
            .card h3 {
                color: #667eea;
                margin-bottom: 20px;
                font-size: 1.4rem;
                font-weight: 600;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            
            .card-icon {
                font-size: 1.6rem;
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
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                border-radius: 8px;
                border-left: 4px solid #667eea;
                transition: transform 0.2s ease;
            }
            
            .stat:hover {
                transform: scale(1.02);
            }
            
            .stat-number {
                font-size: 2.2rem;
                font-weight: 700;
                color: #667eea;
                margin-bottom: 5px;
            }
            
            .stat-label {
                font-size: 0.9rem;
                color: #6c757d;
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
                border-radius: 8px;
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
            }
            
            .btn-primary {
                background: linear-gradient(135deg, #667eea 0%, #5a6fd8 100%);
                color: white;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
            }
            
            .btn-primary:hover {
                background: linear-gradient(135deg, #5a6fd8 0%, #4a5fc8 100%);
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
            }
            
            .btn-secondary {
                background: linear-gradient(135deg, #6c757d 0%, #5a6268 100%);
                color: white;
                box-shadow: 0 4px 15px rgba(108, 117, 125, 0.3);
            }
            
            .btn-secondary:hover {
                background: linear-gradient(135deg, #5a6268 0%, #495057 100%);
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(108, 117, 125, 0.4);
            }
            
            .btn-success {
                background: linear-gradient(135deg, #28a745 0%, #218838 100%);
                color: white;
                box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);
            }
            
            .btn-success:hover {
                background: linear-gradient(135deg, #218838 0%, #1e7e34 100%);
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(40, 167, 69, 0.4);
            }
            
            .btn-warning {
                background: linear-gradient(135deg, #ffc107 0%, #e0a800 100%);
                color: #212529;
                box-shadow: 0 4px 15px rgba(255, 193, 7, 0.3);
            }
            
            .btn-warning:hover {
                background: linear-gradient(135deg, #e0a800 0%, #d39e00 100%);
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(255, 193, 7, 0.4);
            }
            
            .site-list {
                margin-top: 20px;
            }
            
            .site-item {
                background: #f8f9fa;
                border-radius: 8px;
                padding: 20px;
                margin-bottom: 15px;
                border-left: 4px solid #667eea;
                transition: all 0.3s ease;
            }
            
            .site-item:hover {
                background: #e9ecef;
                transform: translateX(5px);
            }
            
            .site-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 10px;
            }
            
            .site-name {
                font-weight: 600;
                color: #495057;
                font-size: 1.1rem;
            }
            
            .site-status {
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 0.8rem;
                font-weight: 600;
                text-transform: uppercase;
            }
            
            .status-active {
                background: #d4edda;
                color: #155724;
            }
            
            .status-inactive {
                background: #f8d7da;
                color: #721c24;
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
                color: #667eea;
                font-size: 1.1rem;
            }
            
            .detail-label {
                color: #6c757d;
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
                background: #f8f9fa;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 10px;
                border-left: 4px solid #28a745;
                transition: all 0.3s ease;
            }
            
            .change-item:hover {
                background: #e9ecef;
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
                color: #495057;
            }
            
            .change-time {
                font-size: 0.8rem;
                color: #6c757d;
            }
            
            .change-summary {
                font-size: 0.9rem;
                color: #6c757d;
            }
            
            .loading {
                text-align: center;
                padding: 40px;
                color: #6c757d;
            }
            
            .spinner {
                border: 4px solid #f3f3f3;
                border-top: 4px solid #667eea;
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
                background: #f8d7da;
                color: #721c24;
                padding: 15px;
                border-radius: 8px;
                margin: 20px 0;
                border-left: 4px solid #dc3545;
            }
            
            .success {
                background: #d4edda;
                color: #155724;
                padding: 15px;
                border-radius: 8px;
                margin: 20px 0;
                border-left: 4px solid #28a745;
            }
            
            .tabs {
                display: flex;
                margin-bottom: 20px;
                border-bottom: 2px solid #e9ecef;
            }
            
            .tab {
                padding: 12px 24px;
                cursor: pointer;
                border-bottom: 2px solid transparent;
                transition: all 0.3s ease;
                font-weight: 600;
            }
            
            .tab.active {
                border-bottom-color: #667eea;
                color: #667eea;
            }
            
            .tab:hover {
                background: #f8f9fa;
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
                background: rgba(255,255,255,0.9);
                padding: 10px 15px;
                border-radius: 8px;
                font-size: 0.9rem;
                color: #667eea;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                z-index: 1000;
                display: none;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🌌 Astral</h1>
                <p>Website Change Detection Dashboard</p>
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
                            🚀 Trigger All Sites
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
                    const response = await fetch('/api/listeners/analytics');
                    const data = await response.json();
                    
                    if (data.status === 'healthy') {
                        const overview = data.analytics.overview;
                        document.getElementById('totalSites').textContent = overview.total_sites;
                        document.getElementById('totalUrls').textContent = overview.total_urls_monitored.toLocaleString();
                        document.getElementById('totalChanges').textContent = overview.total_changes_detected.toLocaleString();
                        document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString();
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
                    const response = await fetch('/api/listeners/changes?limit=10');
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
                                                Trigger
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
                    const response = await fetch(`/api/listeners/trigger/${siteId}`, {
                        method: 'POST'
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        if (data.status === 'started') {
                            showSuccess(`Detection started for ${siteId}. Monitoring progress...`);
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
                            showSuccess(`Successfully triggered detection for ${siteId}`);
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
                    const response = await fetch('/api/listeners/trigger/all', {
                        method: 'POST'
                    });
                    
                    if (response.ok) {
                        showSuccess('Successfully triggered detection for all sites');
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