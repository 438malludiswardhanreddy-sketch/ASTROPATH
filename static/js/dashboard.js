// ASTROPATH - Dashboard JavaScript with Map Integration
let map;
let markersLayer;
let heatmapLayer;
let showHeatmap = false;
let allDetections = [];

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeMap();
    loadDetections();
    updateDashboardStats();

    // Set up event listeners
    document.getElementById('toggle-heatmap')?.addEventListener('click', toggleHeatmap);
    document.getElementById('refresh-map')?.addEventListener('click', loadDetections);
    document.getElementById('filter-severity')?.addEventListener('change', filterDetections);
    document.getElementById('filter-status')?.addEventListener('change', filterDetections);

    // Auto-refresh every 30 seconds
    setInterval(loadDetections, 30000);
    setInterval(updateDashboardStats, 10000);
});

// Initialize Leaflet map
function initializeMap() {
    // Default center (Solapur, India)
    const defaultCenter = [17.6599, 75.9064];

    map = L.map('map').setView(defaultCenter, 13);

    // Add tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19
    }).addTo(map);

    // Initialize marker layer
    markersLayer = L.layerGroup().addTo(map);

    console.log('🗺️  Map initialized');
}

// Load detections from API
async function loadDetections() {
    try {
        const response = await fetch('/api/detections?limit=500');
        const data = await response.json();

        if (data.success) {
            allDetections = data.detections;
            displayDetections(allDetections);
            updateDetectionsList(allDetections);
        }
    } catch (error) {
        console.error('Failed to load detections:', error);
    }
}

// Display detections on map
function displayDetections(detections) {
    // Clear existing markers
    markersLayer.clearLayers();

    // Remove heatmap if exists
    if (heatmapLayer) {
        map.removeLayer(heatmapLayer);
        heatmapLayer = null;
    }

    if (showHeatmap) {
        displayHeatmap(detections);
    } else {
        displayMarkers(detections);
    }

    // Fit map to show all markers
    if (detections.length > 0) {
        const bounds = detections.map(d => [d.latitude, d.longitude]);
        map.fitBounds(bounds, { padding: [50, 50] });
    }
}

// Display individual markers
function displayMarkers(detections) {
    detections.forEach(detection => {
        const color = getSeverityColor(detection.severity);

        const marker = L.circleMarker([detection.latitude, detection.longitude], {
            radius: 8,
            fillColor: color,
            color: '#fff',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.8
        });

        // Create popup
        const popupContent = `
            <div style="min-width: 200px;">
                <h3 style="margin: 0 0 0.5rem 0; color: ${color};">
                    ${detection.severity} Severity
                </h3>
                <p style="margin: 0.25rem 0;">
                    <strong>Location:</strong> ${detection.latitude.toFixed(4)}, ${detection.longitude.toFixed(4)}
                </p>
                <p style="margin: 0.25rem 0;">
                    <strong>Confidence:</strong> ${(detection.confidence * 100).toFixed(1)}%
                </p>
                <p style="margin: 0.25rem 0;">
                    <strong>Time:</strong> ${new Date(detection.timestamp).toLocaleString()}
                </p>
                <p style="margin: 0.25rem 0;">
                    <strong>Source:</strong> ${detection.source}
                </p>
                ${detection.status ? `<p style="margin: 0.25rem 0;"><strong>Status:</strong> ${detection.status}</p>` : ''}
            </div>
        `;

        marker.bindPopup(popupContent);
        markersLayer.addLayer(marker);
    });
}

// Display heatmap
function displayHeatmap(detections) {
    const heatData = detections.map(d => [
        d.latitude,
        d.longitude,
        d.severity === 'High' ? 1.0 : d.severity === 'Medium' ? 0.6 : 0.3
    ]);

    heatmapLayer = L.heatLayer(heatData, {
        radius: 25,
        blur: 35,
        maxZoom: 17,
        max: 1.0,
        gradient: {
            0.0: 'green',
            0.5: 'yellow',
            0.7: 'orange',
            1.0: 'red'
        }
    }).addTo(map);
}

// Toggle heatmap view
function toggleHeatmap() {
    showHeatmap = !showHeatmap;
    const button = document.getElementById('toggle-heatmap');

    if (showHeatmap) {
        button.innerHTML = '<i class="fas fa-map-marker-alt"></i> Markers';
    } else {
        button.innerHTML = '<i class="fas fa-fire"></i> Heatmap';
    }

    displayDetections(allDetections);
}

// Filter detections by severity and status
function filterDetections() {
    const severity = document.getElementById('filter-severity').value;
    const status = document.getElementById('filter-status').value;

    let filtered = allDetections;

    if (severity !== 'all') {
        filtered = filtered.filter(d => d.severity === severity);
    }

    if (status !== 'all') {
        filtered = filtered.filter(d => d.repair_status === status);
    }

    displayDetections(filtered);
    updateDetectionsList(filtered);
}

// Update detections list/table
function updateDetectionsList(detections) {
    const container = document.getElementById('detections-table');

    if (detections.length === 0) {
        container.innerHTML = '<p class="no-data">No detections found</p>';
        return;
    }

    container.innerHTML = detections.map(det => `
        <div class="detection-card severity-${det.severity.toLowerCase()}" onclick="openDetailPanel(${det.id})">
            <div class="card-header">
                <span class="badge severity-${det.severity.toLowerCase()}">${det.severity}</span>
                <span class="status-indicator status-${det.repair_status || 'pending'}"></span>
            </div>
            <div class="card-body">
                <strong>${new Date(det.timestamp).toLocaleTimeString()}</strong>
                <p>${det.latitude.toFixed(4)}, ${det.longitude.toFixed(4)}</p>
                <p class="source">${det.source} | ${(det.confidence * 100).toFixed(0)}%</p>
            </div>
        </div>
    `).join('');
}

// Focus map on specific detection
function focusOnDetection(lat, lon) {
    if (!map) return;
    map.setView([lat, lon], 16);

    // Find and open popup for this marker if any
    markersLayer.eachLayer(layer => {
        const latlng = layer.getLatLng();
        if (Math.abs(latlng.lat - lat) < 0.0001 && Math.abs(latlng.lng - lon) < 0.0001) {
            layer.openPopup();
        }
    });
}

// Update dashboard statistics
async function updateDashboardStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();

        if (data.success) {
            const stats = data.stats;
            document.getElementById('total-count').textContent = stats.total_detections || 0;
            document.getElementById('high-severity').textContent = stats.high_severity || 0;
            document.getElementById('resolved-count').textContent = stats.repairs_completed || 0;
        }
    } catch (error) {
        console.error('Failed to update stats:', error);
    }
}

// Get severity color
function getSeverityColor(severity) {
    switch (severity) {
        case 'High': return '#ef4444'; // Red 500
        case 'Medium': return '#f59e0b'; // Amber 500
        case 'Low': return '#10b981'; // Emerald 500
        default: return '#64748b'; // Slate 500
    }
}

// Open detail panel for a detection
function openDetailPanel(id) {
    const det = allDetections.find(d => d.id === id);
    if (!det) return;

    // Focus on map
    focusOnDetection(det.latitude, det.longitude);

    const panel = document.getElementById('detail-panel');
    const content = document.getElementById('detail-content');

    panel.classList.add('active');

    content.innerHTML = `
        <div class="detail-image">
            ${det.image_path ? `<img src="/${det.image_path}" alt="Pothole">` : '<div class="no-image"><i class="fas fa-image"></i> No image available</div>'}
        </div>
        <div class="detail-info">
            <div class="info-row">
                <span class="label">Time</span>
                <span class="value">${new Date(det.timestamp).toLocaleString()}</span>
            </div>
            <div class="info-row">
                <span class="label">Coordinates</span>
                <span class="value">${det.latitude.toFixed(6)}, ${det.longitude.toFixed(6)}</span>
            </div>
            <div class="info-row">
                <span class="label">Severity</span>
                <span class="value severity-${det.severity.toLowerCase()}">${det.severity}</span>
            </div>
            <div class="info-row">
                <span class="label">Source</span>
                <span class="value">${det.source}</span>
            </div>
            <div class="info-row">
                <span class="label">Status</span>
                <span class="value status-text-${det.repair_status || 'pending'}">${(det.repair_status || 'pending').replace('_', ' ')}</span>
            </div>
        </div>
        
        <div class="detail-actions">
            <h4>Update Status</h4>
            <div class="action-buttons">
                <button class="btn btn-warning btn-sm" onclick="updateStatus(${det.id}, 'pending')">Pending</button>
                <button class="btn btn-info btn-sm" onclick="updateStatus(${det.id}, 'in_progress')">Investigating</button>
                <button class="btn btn-success btn-sm" onclick="updateStatus(${det.id}, 'completed')">Resolved</button>
            </div>
            <textarea id="status-notes" placeholder="Add notes here...">${det.notes || ''}</textarea>
        </div>
    `;
}

// Close detail panel
function closeDetailPanel() {
    document.getElementById('detail-panel').classList.remove('active');
}

// Update detection status via API
async function updateStatus(id, status) {
    const notes = document.getElementById('status-notes')?.value || "";

    try {
        const response = await fetch(`/api/detections/${id}/status`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status, notes })
        });

        const data = await response.json();
        if (data.success) {
            // Reload data
            await loadDetections();
            await updateDashboardStats();
            // Refresh details
            openDetailPanel(id);
        } else {
            alert("Failed to update status: " + data.error);
        }
    } catch (error) {
        console.error("Error updating status:", error);
    }
}

// Export functions
window.focusOnDetection = focusOnDetection;
window.openDetailPanel = openDetailPanel;
window.closeDetailPanel = closeDetailPanel;
window.updateStatus = updateStatus;
