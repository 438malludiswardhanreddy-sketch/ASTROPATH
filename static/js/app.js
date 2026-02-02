// ASTROPATH - Main Application JavaScript
let detectionActive = false;
let currentLocation = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
    updateStats();
    updateLocation();
    loadRecentDetections();
    
    // Set up event listeners
    document.getElementById('toggle-detection')?.addEventListener('click', toggleDetection);
    document.getElementById('camera-source')?.addEventListener('change', changeCamera);
    document.getElementById('upload-form')?.addEventListener('submit', handleUpload);
    document.getElementById('pothole-image')?.addEventListener('change', previewImage);
    
    // Update stats every 5 seconds
    setInterval(updateStats, 5000);
    setInterval(loadRecentDetections, 10000);
});

// Initialize application
async function initializeApp() {
    console.log('🚀 ASTROPATH Application initialized');
    
    // Check system health
    try {
        const response = await fetch('/health');
        const health = await response.json();
        
        document.getElementById('system-status').textContent = 
            health.status === 'healthy' ? 'Active' : 'Offline';
        
        if (health.gps_connected) {
            document.getElementById('gps-status').textContent = 'Connected';
        } else if (health.gps_enabled) {
            document.getElementById('gps-status').textContent = 'Enabled';
        } else {
            document.getElementById('gps-status').textContent = 'IP-based';
        }
    } catch (error) {
        console.error('Health check failed:', error);
        document.getElementById('system-status').textContent = 'Error';
    }
}

// Update statistics
async function updateStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        
        if (data.success) {
            const stats = data.stats;
            document.getElementById('total-detections').textContent = stats.total || 0;
        }
    } catch (error) {
        console.error('Failed to update stats:', error);
    }
}

// Update current location
async function updateLocation() {
    try {
        const response = await fetch('/api/location');
        const data = await response.json();
        
        if (data.success) {
            currentLocation = {
                latitude: data.latitude,
                longitude: data.longitude,
                source: data.source
            };
            
            const locationText = `${data.latitude.toFixed(4)}, ${data.longitude.toFixed(4)}`;
            document.getElementById('current-location').textContent = locationText;
            
            // Update upload modal location if exists
            const uploadLocation = document.getElementById('upload-location');
            if (uploadLocation) {
                uploadLocation.textContent = `${locationText} (${data.source})`;
            }
        }
    } catch (error) {
        console.error('Failed to get location:', error);
        document.getElementById('current-location').textContent = 'Unavailable';
    }
}

// Toggle detection
function toggleDetection() {
    const button = document.getElementById('toggle-detection');
    const videoFeed = document.getElementById('video-feed');
    const cameraSource = document.getElementById('camera-source').value;
    
    if (!detectionActive) {
        // Start detection
        detectionActive = true;
        button.innerHTML = '<i class="fas fa-stop"></i> Stop Detection';
        button.style.background = 'linear-gradient(135deg, #f5576c 0%, #f093fb 100%)';
        
        // Start video feed
        videoFeed.src = `/video_feed?source=${cameraSource}&t=${Date.now()}`;
        
        // Notify backend
        fetch('/api/start_detection', { method: 'POST' })
            .then(response => response.json())
            .then(data => console.log('Detection started:', data))
            .catch(error => console.error('Failed to start detection:', error));
            
    } else {
        // Stop detection
        detectionActive = false;
        button.innerHTML = '<i class="fas fa-play"></i> Start Detection';
        button.style.background = '';
        
        // Stop video feed
        videoFeed.src = '';
        
        // Notify backend
        fetch('/api/stop_detection', { method: 'POST' })
            .then(response => response.json())
            .then(data => console.log('Detection stopped:', data))
            .catch(error => console.error('Failed to stop detection:', error));
    }
}

// Change camera source
function changeCamera() {
    if (detectionActive) {
        // Restart with new source
        toggleDetection();
        setTimeout(toggleDetection, 500);
    }
}

// Load recent detections
async function loadRecentDetections() {
    try {
        const response = await fetch('/api/detections?limit=10');
        const data = await response.json();
        
        if (data.success && data.detections.length > 0) {
            const container = document.getElementById('detections-list');
            
            container.innerHTML = data.detections.map(det => `
                <div class="detection-item">
                    <span class="severity-badge severity-${det.severity.toLowerCase()}">
                        ${det.severity}
                    </span>
                    <div>
                        <strong>${new Date(det.timestamp).toLocaleString()}</strong>
                        <p style="color: var(--text-secondary); font-size: 0.85rem;">
                            Location: ${det.latitude.toFixed(4)}, ${det.longitude.toFixed(4)}
                        </p>
                    </div>
                    <div style="text-align: right; color: var(--text-secondary);">
                        <small>Confidence: ${(det.confidence * 100).toFixed(1)}%</small>
                    </div>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Failed to load detections:', error);
    }
}

// Show upload modal
function showUploadModal() {
    const modal = document.getElementById('upload-modal');
    modal.classList.add('active');
    updateLocation(); // Refresh location
}

// Close upload modal
function closeUploadModal() {
    const modal = document.getElementById('upload-modal');
    modal.classList.remove('active');
    document.getElementById('upload-form').reset();
    document.getElementById('image-preview').innerHTML = '';
}

// Preview image
function previewImage(event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById('image-preview').innerHTML = 
                `<img src="${e.target.result}" alt="Preview">`;
        };
        reader.readAsDataURL(file);
    }
}

// Handle upload form submission
async function handleUpload(event) {
    event.preventDefault();
    
    const fileInput = document.getElementById('pothole-image');
    const severity = document.getElementById('severity').value;
    const description = document.getElementById('description').value;
    
    if (!fileInput.files[0]) {
        showNotification('Please select an image', 'error');
        return;
    }
    
    // Read image as base64
    const reader = new FileReader();
    reader.onload = async function(e) {
        const imageData = e.target.result;
        
        try {
            const response = await fetch('/api/upload', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    image: imageData,
                    severity: severity,
                    description: description,
                    latitude: currentLocation?.latitude,
                    longitude: currentLocation?.longitude
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                showNotification('Report submitted successfully!', 'success');
                closeUploadModal();
                loadRecentDetections(); // Refresh list
            } else {
                showNotification('Failed to submit report: ' + data.error, 'error');
            }
        } catch (error) {
            console.error('Upload error:', error);
            showNotification('Network error. Please try again.', 'error');
        }
    };
    
    reader.readAsDataURL(fileInput.files[0]);
}

// Show notification
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? 'var(--success-color)' : 'var(--danger-color)'};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 0.5rem;
        box-shadow: var(--shadow);
        z-index: 3000;
        animation: slideIn 0.3s ease;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Add animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Close modal on background click
document.addEventListener('click', (e) => {
    const modal = document.getElementById('upload-modal');
    if (e.target === modal) {
        closeUploadModal();
    }
});

// Handle escape key to close modal
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeUploadModal();
    }
});
