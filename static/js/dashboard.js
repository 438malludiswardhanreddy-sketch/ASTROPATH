/* ASTROPATH Dashboard JavaScript */

// Global variables
let map;
let detections = [];
let markers = {};
let selectedDetection = null;
let autoRefreshInterval = null;

// Initialize dashboard on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing ASTROPATH Dashboard...');
    initializeMap();
    loadDetections();
    setupEventListeners();
    
    // Auto-refresh checkbox
    const autoRefreshCheckbox = document.getElementById('autoRefresh');
    if (autoRefreshCheckbox.checked) {
        startAutoRefresh();
    }
});

/**
 * Initialize Leaflet map
 */
function initializeMap() {
    // Default center (Solapur, Maharashtra)
    const defaultCenter = [17.6726, 75.8456];
    
    map = L.map('map').setView(defaultCenter, 13);
    
    // Add base layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19,
        minZoom: 10
    }).addTo(map);
    
    console.log('Map initialized');
}

/**
 * Load detections from API
 */
async function loadDetections() {
    try {
        // Get filter values
        const severity = document.getElementById('severityFilter').value;
        const hours = document.getElementById('hoursFilter').value;
        
        let url = '/api/detections?limit=500';
        if (severity) url += `&severity=${severity}`;
        if (hours) url += `&hours=${hours}`;
        
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.status === 'success') {
            detections = data.detections;
            console.log(`Loaded ${detections.length} detections`);
            
            // Update display
            updateMap();
            updateList();
            updateStatistics();
            updateHeader();
        } else {
            console.error('API error:', data.message);
        }
    } catch (error) {
        console.error('Error loading detections:', error);
    }
}

/**
 * Update map markers
 */
function updateMap() {
    // Clear existing markers
    Object.values(markers).forEach(marker => map.removeLayer(marker));
    markers = {};
    
    // Add new markers
    detections.forEach(detection => {
        const lat = parseFloat(detection.latitude);
        const lon = parseFloat(detection.longitude);
        const severity = detection.severity.toLowerCase();
        
        if (isNaN(lat) || isNaN(lon)) {
            console.warn('Invalid coordinates:', detection);
            return;
        }
        
        // Choose color based on severity
        const color = {
            'high': '#e74c3c',
            'medium': '#f39c12',
            'low': '#16a085'
        }[severity] || '#95a5a6';
        
        // Create circle marker
        const marker = L.circleMarker([lat, lon], {
            radius: severity === 'high' ? 8 : (severity === 'medium' ? 6 : 4),
            fillColor: color,
            color: color,
            weight: 2,
            opacity: 0.8,
            fillOpacity: 0.7
        }).addTo(map);
        
        // Add popup and click handler
        marker.bindPopup(`
            <div class="marker-popup">
                <strong>${detection.severity} Severity</strong><br>
                Location: ${lat.toFixed(4)}, ${lon.toFixed(4)}<br>
                Confidence: ${(detection.confidence * 100).toFixed(1)}%<br>
                <small>${new Date(detection.timestamp).toLocaleString()}</small>
            </div>
        `);
        
        marker.on('click', function() {
            showDetectionDetail(detection.id);
        });
        
        markers[detection.id] = marker;
    });
    
    // Fit map to markers if any exist
    if (detections.length > 0) {
        const bounds = Object.values(markers).map(m => m.getLatLng());
        if (bounds.length > 0) {
            const group = new L.featureGroup(Object.values(markers));
            map.fitBounds(group.getBounds().pad(0.1));
        }
    }
}

/**
 * Update detections list
 */
function updateList() {
    const list = document.getElementById('detectionsList');
    
    if (detections.length === 0) {
        list.innerHTML = '<div class="loading">No detections found</div>';
        return;
    }
    
    list.innerHTML = detections.map(detection => {
        const date = new Date(detection.timestamp);
        const severity = detection.severity.toLowerCase();
        const statusColor = {
            'pending': '#95a5a6',
            'in_progress': '#f39c12',
            'completed': '#27ae60'
        }[detection.repair_status] || '#95a5a6';
        
        return `
            <div class="detection-card ${severity}" onclick="showDetectionDetail(${detection.id})">
                <div class="detection-info">
                    <div class="detection-location">
                        📍 ${parseFloat(detection.latitude).toFixed(4)}, ${parseFloat(detection.longitude).toFixed(4)}
                    </div>
                    <div class="detection-meta">
                        <span class="detection-badge ${severity}">${detection.severity}</span>
                        <span>Confidence: ${(detection.confidence * 100).toFixed(0)}%</span>
                        <span>${date.toLocaleString()}</span>
                    </div>
                </div>
                <div>
                    <span style="font-size: 12px; padding: 4px 8px; border-radius: 3px; background-color: ${statusColor}20; color: ${statusColor}; font-weight: 600;">
                        ${detection.repair_status.toUpperCase()}
                    </span>
                </div>
            </div>
        `;
    }).join('');
}

/**
 * Update statistics display
 */
async function updateStatistics() {
    try {
        const response = await fetch('/api/statistics?days=30');
        const data = await response.json();
        
        if (data.status === 'success') {
            const stats = data.statistics;
            
            document.getElementById('highCount').textContent = stats.high_severity || 0;
            document.getElementById('mediumCount').textContent = stats.medium_severity || 0;
            document.getElementById('lowCount').textContent = stats.low_severity || 0;
        }
    } catch (error) {
        console.error('Error loading statistics:', error);
    }
}

/**
 * Update header statistics
 */
function updateHeader() {
    // Total detections
    document.getElementById('totalDetections').textContent = detections.length;
    
    // Pending repairs
    const pending = detections.filter(d => d.repair_status === 'pending').length;
    document.getElementById('pendingRepairs').textContent = pending;
    
    // Last updated
    const now = new Date();
    document.getElementById('lastUpdated').textContent = 
        now.getHours().toString().padStart(2, '0') + ':' + 
        now.getMinutes().toString().padStart(2, '0');
}

/**
 * Show detection detail in modal
 */
async function showDetectionDetail(detectionId) {
    try {
        const response = await fetch(`/api/detections/${detectionId}`);
        const data = await response.json();
        
        if (data.status === 'success') {
            const det = data.detection;
            selectedDetection = det;
            
            const date = new Date(det.timestamp);
            const gpsQualityDesc = {
                0: 'No Fix',
                1: 'GPS Fix',
                2: 'DGPS Fix',
                3: 'PPS Fix',
                4: 'Real-time Kinematic',
                5: 'Float RTK',
                6: 'Estimated',
                7: 'Manual',
                8: 'Simulation'
            }[det.gps_quality] || 'Unknown';
            
            const modal = document.getElementById('detailModal');
            const modalBody = document.getElementById('modalBody');
            
            modalBody.innerHTML = `
                <div class="modal-detail">
                    <div class="modal-detail-label">📍 Location</div>
                    <div class="modal-detail-value">
                        Latitude: ${parseFloat(det.latitude).toFixed(6)}<br>
                        Longitude: ${parseFloat(det.longitude).toFixed(6)}
                    </div>
                </div>
                
                <div class="modal-detail">
                    <div class="modal-detail-label">🛰️ GPS Information</div>
                    <div class="modal-detail-value">
                        Quality: ${gpsQualityDesc} (${det.gps_quality})<br>
                        Timestamp: ${date.toLocaleString()}
                    </div>
                </div>
                
                <div class="modal-detail">
                    <div class="modal-detail-label">🚨 Detection Details</div>
                    <div class="modal-detail-value">
                        Severity: <span style="color: #e74c3c; font-weight: bold;">${det.severity}</span><br>
                        Confidence: ${(det.confidence * 100).toFixed(1)}%<br>
                        Class: ${det.class_name}
                    </div>
                </div>
                
                <div class="modal-detail">
                    <div class="modal-detail-label">🔧 Repair Status</div>
                    <div class="modal-detail-value">
                        Status: ${det.repair_status.toUpperCase()}<br>
                        ${det.notes ? `Notes: ${det.notes}<br>` : ''}
                        ${det.repair_date ? `Repair Date: ${det.repair_date}` : ''}
                    </div>
                </div>
                
                <div class="modal-detail">
                    <div class="modal-detail-label">📷 Camera Source</div>
                    <div class="modal-detail-value">${det.camera_source || 'Unknown'}</div>
                </div>
            `;
            
            modal.classList.add('show');
        }
    } catch (error) {
        console.error('Error fetching detection detail:', error);
    }
}

/**
 * Close modal
 */
function closeModal() {
    document.getElementById('detailModal').classList.remove('show');
}

/**
 * Update repair status
 */
async function updateRepairStatus() {
    if (!selectedDetection) return;
    
    try {
        const response = await fetch(`/api/detections/${selectedDetection.id}/status`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                status: 'completed',
                notes: 'Marked as repaired from dashboard'
            })
        });
        
        const data = await response.json();
        if (data.status === 'success') {
            alert('Repair status updated!');
            closeModal();
            loadDetections();
        }
    } catch (error) {
        console.error('Error updating repair status:', error);
        alert('Error updating repair status');
    }
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Filters
    document.getElementById('applyFilter').addEventListener('click', loadDetections);
    
    // Refresh button
    document.getElementById('refreshBtn').addEventListener('click', loadDetections);
    
    // Auto-refresh checkbox
    document.getElementById('autoRefresh').addEventListener('change', function(e) {
        if (e.target.checked) {
            startAutoRefresh();
        } else {
            stopAutoRefresh();
        }
    });
    
    // Modal close button
    document.querySelector('.modal-close').addEventListener('click', closeModal);
    
    // Close modal when clicking outside
    document.getElementById('detailModal').addEventListener('click', function(e) {
        if (e.target === this) {
            closeModal();
        }
    });
}

/**
 * Start auto-refresh
 */
function startAutoRefresh() {
    console.log('Starting auto-refresh...');
    autoRefreshInterval = setInterval(loadDetections, 30000); // 30 seconds
}

/**
 * Stop auto-refresh
 */
function stopAutoRefresh() {
    console.log('Stopping auto-refresh...');
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
        autoRefreshInterval = null;
    }
}

// Handle page visibility (pause refresh when tab not visible)
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        stopAutoRefresh();
    } else {
        const autoRefreshCheckbox = document.getElementById('autoRefresh');
        if (autoRefreshCheckbox && autoRefreshCheckbox.checked) {
            startAutoRefresh();
        }
    }
});
