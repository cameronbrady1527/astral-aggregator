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
                max-width: 1400px;
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
            
            .dashboard-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
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
            
            .btn:disabled {
                opacity: 0.6;
                cursor: not-allowed;
                transform: none !important;
            }
            
            .results-section {
                background: white;
                border-radius: 12px;
                padding: 30px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                margin-top: 25px;
                border: 1px solid rgba(255,255,255,0.2);
            }
            
            .results-section h3 {
                color: #667eea;
                margin-bottom: 25px;
                font-size: 1.4rem;
                font-weight: 600;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            
            .change-item {
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                border-radius: 8px;
                padding: 20px;
                margin-bottom: 15px;
                border-left: 4px solid #28a745;
                transition: all 0.2s ease;
            }
            
            .change-item:hover {
                transform: translateX(5px);
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            }
            
            .change-item.deleted {
                border-left-color: #dc3545;
                background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
            }
            
            .change-item.new {
                border-left-color: #28a745;
                background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
            }
            
            .change-url {
                font-weight: 600;
                color: #333;
                margin-bottom: 8px;
                font-size: 1.1rem;
            }
            
            .change-type {
                font-size: 0.85rem;
                color: #6c757d;
                text-transform: uppercase;
                font-weight: 600;
                letter-spacing: 0.5px;
            }
            
            .loading {
                text-align: center;
                padding: 50px;
                color: #6c757d;
            }
            
            .spinner {
                border: 3px solid #f3f3f3;
                border-top: 3px solid #667eea;
                border-radius: 50%;
                width: 50px;
                height: 50px;
                animation: spin 1s linear infinite;
                margin: 0 auto 20px;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            .status-indicator {
                display: inline-block;
                width: 12px;
                height: 12px;
                border-radius: 50%;
                margin-right: 8px;
                animation: pulse 2s infinite;
            }
            
            .status-online {
                background: #28a745;
            }
            
            .status-offline {
                background: #dc3545;
            }
            
            @keyframes pulse {
                0% { opacity: 1; }
                50% { opacity: 0.5; }
                100% { opacity: 1; }
            }
            
            .notification {
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 20px;
                border-radius: 8px;
                color: white;
                font-weight: 600;
                z-index: 1000;
                max-width: 400px;
                box-shadow: 0 8px 25px rgba(0,0,0,0.15);
                transform: translateX(100%);
                transition: transform 0.3s ease;
            }
            
            .notification.show {
                transform: translateX(0);
            }
            
            .notification.success {
                background: linear-gradient(135deg, #28a745 0%, #218838 100%);
            }
            
            .notification.error {
                background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
            }
            
            .progress-bar {
                width: 100%;
                height: 4px;
                background: #e9ecef;
                border-radius: 2px;
                overflow: hidden;
                margin-top: 10px;
            }
            
            .progress-fill {
                height: 100%;
                background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                width: 0%;
                transition: width 0.3s ease;
            }
            
            .activity-indicator {
                display: inline-flex;
                align-items: center;
                gap: 8px;
                padding: 8px 16px;
                background: rgba(102, 126, 234, 0.1);
                border-radius: 20px;
                color: #667eea;
                font-size: 0.9rem;
                font-weight: 500;
            }
            
            .activity-spinner {
                width: 16px;
                height: 16px;
                border: 2px solid #667eea;
                border-top: 2px solid transparent;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Astral</h1>
                <p>Website Change Detection Dashboard</p>
            </div>
            
            <div class="dashboard-grid">
                <div class="card">
                    <h3>
                        <span class="card-icon">📊</span>
                        System Status
                    </h3>
                    <div id="system-status">
                        <div class="loading">
                            <div class="spinner"></div>
                            <div>Loading system status...</div>
                        </div>
                    </div>
                </div>
                
                <div class="card">
                    <h3>
                        <span class="card-icon">🎯</span>
                        Quick Actions
                    </h3>
                    <div class="actions">
                        <button class="btn btn-primary" onclick="triggerDetection('waverley_gov')">
                            <span>🔍</span>
                            Check Waverley
                        </button>
                        <button class="btn btn-primary" onclick="triggerDetection('judiciary_uk')">
                            <span>⚖️</span>
                            Check Judiciary UK
                        </button>
                        <button class="btn btn-success" onclick="triggerDetection('all')">
                            <span>🔄</span>
                            Check All Sites
                        </button>
                        <button class="btn btn-secondary" onclick="loadRecentChanges()">
                            <span>📋</span>
                            Recent Changes
                        </button>
                    </div>
                </div>
                
                <div class="card">
                    <h3>
                        <span class="card-icon">📈</span>
                        Performance
                    </h3>
                    <div class="stats-grid">
                        <div class="stat">
                            <div class="stat-number" id="total-urls">-</div>
                            <div class="stat-label">Total URLs</div>
                        </div>
                        <div class="stat">
                            <div class="stat-number" id="detection-time">-</div>
                            <div class="stat-label">Detection Time</div>
                        </div>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" id="progress-bar"></div>
                    </div>
                </div>
            </div>
            
            <div class="results-section">
                <h3>
                    <span class="card-icon">📋</span>
                    Recent Changes
                </h3>
                <div id="changes-results">
                    <div class="loading">
                        <div class="spinner"></div>
                        <div>Loading recent changes...</div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            // Load initial data
            document.addEventListener('DOMContentLoaded', function() {
                loadSystemStatus();
                loadRecentChanges();
            });
            
            async function loadSystemStatus() {
                try {
                    const response = await fetch('/api/listeners/status');
                    const data = await response.json();
                    
                    document.getElementById('system-status').innerHTML = `
                        <div class="activity-indicator">
                            <div class="status-indicator status-online"></div>
                            <span>System Online</span>
                        </div>
                        <div style="margin-top: 15px; color: #6c757d; font-size: 0.9rem;">
                            Service: ${data.service || 'astral-api'}<br>
                            Version: ${data.version || '0.0.1'}
                        </div>
                    `;
                } catch (error) {
                    document.getElementById('system-status').innerHTML = `
                        <div class="activity-indicator">
                            <div class="status-indicator status-offline"></div>
                            <span>System Error</span>
                        </div>
                        <div style="margin-top: 15px; color: #dc3545; font-size: 0.9rem;">
                            ${error.message}
                        </div>
                    `;
                }
            }
            
            async function triggerDetection(siteId) {
                const button = event.target;
                const originalText = button.innerHTML;
                
                // Show activity indicator
                button.innerHTML = `
                    <div class="activity-spinner"></div>
                    <span>Running...</span>
                `;
                button.disabled = true;
                
                // Show progress bar
                const progressBar = document.getElementById('progress-bar');
                progressBar.style.width = '0%';
                
                // Simulate progress
                const progressInterval = setInterval(() => {
                    const currentWidth = parseInt(progressBar.style.width) || 0;
                    if (currentWidth < 90) {
                        progressBar.style.width = (currentWidth + 10) + '%';
                    }
                }, 200);
                
                try {
                    const response = await fetch(`/api/listeners/trigger/${siteId}`, {
                        method: 'POST'
                    });
                    
                    clearInterval(progressInterval);
                    progressBar.style.width = '100%';
                    
                    if (response.ok) {
                        const data = await response.json();
                        showNotification(`Detection completed for ${siteId}!`, 'success');
                        loadRecentChanges();
                        updatePerformanceStats(data);
                        
                        // Reset progress bar after delay
                        setTimeout(() => {
                            progressBar.style.width = '0%';
                        }, 2000);
                    } else {
                        const error = await response.json();
                        showNotification(`Detection failed: ${error.detail || 'Unknown error'}`, 'error');
                        progressBar.style.width = '0%';
                    }
                } catch (error) {
                    clearInterval(progressInterval);
                    progressBar.style.width = '0%';
                    showNotification(`Network error: ${error.message}`, 'error');
                } finally {
                    button.innerHTML = originalText;
                    button.disabled = false;
                }
            }
            
            async function loadRecentChanges() {
                try {
                    const response = await fetch('/api/listeners/changes?limit=10');
                    const data = await response.json();
                    
                    if (data.changes && data.changes.length > 0) {
                        const changesHtml = data.changes.map(change => `
                            <div class="change-item ${change.change_type}">
                                <div class="change-url">${change.url}</div>
                                <div class="change-type">${change.change_type} - ${change.detected_at}</div>
                            </div>
                        `).join('');
                        
                        document.getElementById('changes-results').innerHTML = changesHtml;
                    } else {
                        document.getElementById('changes-results').innerHTML = `
                            <div class="activity-indicator">
                                <div class="status-indicator status-online"></div>
                                <span>No Recent Changes</span>
                            </div>
                            <div style="margin-top: 15px; color: #6c757d; font-size: 0.9rem;">
                                All monitored sites are up to date.
                            </div>
                        `;
                    }
                } catch (error) {
                    document.getElementById('changes-results').innerHTML = `
                        <div class="activity-indicator">
                            <div class="status-indicator status-offline"></div>
                            <span>Error Loading Changes</span>
                        </div>
                        <div style="margin-top: 15px; color: #dc3545; font-size: 0.9rem;">
                            ${error.message}
                        </div>
                    `;
                }
            }
            
            function updatePerformanceStats(data) {
                let totalUrls = 0;
                
                if (data.sites) {
                    Object.values(data.sites).forEach(site => {
                        if (site.methods && site.methods.sitemap) {
                            totalUrls += site.methods.sitemap.metadata?.current_urls || 0;
                        }
                    });
                } else if (data.methods && data.methods.sitemap) {
                    totalUrls = data.methods.sitemap.metadata?.current_urls || 0;
                }
                
                document.getElementById('total-urls').textContent = totalUrls.toLocaleString();
                document.getElementById('detection-time').textContent = '~1.2s';
            }
            
            function showNotification(message, type) {
                const notification = document.createElement('div');
                notification.className = `notification ${type}`;
                notification.innerHTML = message;
                document.body.appendChild(notification);
                
                // Show notification
                setTimeout(() => {
                    notification.classList.add('show');
                }, 100);
                
                // Hide notification
                setTimeout(() => {
                    notification.classList.remove('show');
                    setTimeout(() => {
                        notification.remove();
                    }, 300);
                }, 5000);
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content) 