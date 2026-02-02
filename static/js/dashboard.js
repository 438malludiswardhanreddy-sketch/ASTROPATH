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

// Filter detections by severity
function filterDetections() {
    const severity = document.getElementById('filter-severity').value;

    if (severity === 'all') {
        displayDetections(allDetections);
        updateDetectionsList(allDetections);
    } else {
        const filtered = allDetections.filter(d => d.severity === severity);
        displayDetections(filtered);
        updateDetectionsList(filtered);
    }
}

// Update detections list/table
function updateDetectionsList(detections) {
    const container = document.getElementById('detections-table');

    if (detections.length === 0) {
        container.innerHTML = '<p class="no-data">No detections found</p>';
        return;
    }

    container.innerHTML = detections.map(det => `
        <div class="detection-item" onclick="focusOnDetection(${det.latitude}, ${det.longitude})">
            <span class="severity-badge severity-${det.severity.toLowerCase()}">
                ${det.severity}
            </span>
            <div>
                <strong>${new Date(det.timestamp).toLocaleString()}</strong>
                <p style="color: var(--text-secondary); font-size: 0.85rem;">
                    ${det.latitude.toFixed(4)}, ${det.longitude.toFixed(4)}
                </p>
                <p style="color: var(--text-secondary); font-size: 0.85rem;">
                    ${det.source} | ${(det.confidence * 100).toFixed(1)}% confidence
                </p>
            </div>
        </div>
    `).join('');
}

// Focus map on specific detection
function focusOnDetection(lat, lon) {
    map.setView([lat, lon], 16);

    // Find and open popup for this marker
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

            document.getElementById('total-count').textContent = stats.total || 0;
            document.getElementById('high-severity').textContent = stats.high_severity || 0;
            document.getElementById('today-count').textContent = stats.today || 0;
            document.getElementById('resolved-count').textContent = stats.resolved || 0;
        }
    } catch (error) {
        console.error('Failed to update stats:', error);
    }
}

// Get severity color
function getSeverityColor(severity) {
    switch (severity) {
        case 'High':
            return '#ff0000';
        case 'Medium':
            return '#ffa500';
        case 'Low':
            return '#00ff00';
        default:
            return '#888888';
    }
}

// Export functions for global access
window.focusOnDetection = focusOnDetection;
