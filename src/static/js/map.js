let map;
let markers = [];
let markerClusterGroup = null;
let showingTop5 = false;

function initMap() {
    map = L.map('map').setView([-6.2088, 106.8456], 10);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);
    loadMapData();
}

function clearMap() {
    if (!map) return;
    
    if (markerClusterGroup) {
        map.removeLayer(markerClusterGroup);
        markerClusterGroup = null;
    }
    
    markers.forEach(marker => {
        if (map.hasLayer(marker)) {
            map.removeLayer(marker);
        }
    });
    
    markers = [];
    map.setView([-6.2088, 106.8456], 10);
}

function getMarkerColor(coord, top5Stores) {
    if (coord.is_top_5) {
        const storeInfo = top5Stores.find(s => s.store_id === coord.store_id);
        return storeInfo ? storeInfo.color : '#3388ff';
    }
    return '#3388ff';
}

function displayPoints(data, showOnlyTop5 = false) {
    clearMap();
    
    const coordinates = showOnlyTop5 
        ? data.coordinates.filter(coord => coord.is_top_5)
        : data.coordinates;

    // Implement clustering only if more than 20000 points
    if (coordinates.length > 20000) {
        console.log(`Using clustering for ${coordinates.length} points`);
        markerClusterGroup = L.markerClusterGroup({
            chunkedLoading: true,
            maxClusterRadius: 50,
            spiderfyOnMaxZoom: true,
            showCoverageOnHover: false
        });

        // Add points in batches to prevent UI blocking
        const batchSize = 1000;
        for (let i = 0; i < coordinates.length; i += batchSize) {
            setTimeout(() => {
                const batch = coordinates.slice(i, i + batchSize);
                batch.forEach(coord => {
                    const color = getMarkerColor(coord, data.top_5_stores);
                    const marker = L.circleMarker([coord.latitude, coord.longitude], {
                        radius: coord.is_top_5 ? 6 : 4,
                        color: color,
                        fillColor: color,
                        fillOpacity: 0.7
                    });
                    
                    marker.bindPopup(`
                        <b>${coord.store_name}</b><br>
                        Store_ID: ${coord.store_id}<br>
                        Visitor: ${coord.full_name}<br>
                        Date: ${coord.tanggal}
                        ${coord.is_top_5 ? '<br><strong style="color: ' + color + '">Top 5 Most Visited!</strong>' : ''}
                    `);
                    
                    markerClusterGroup.addLayer(marker);
                });
                
                // Fit bounds after last batch
                if (i + batchSize >= coordinates.length) {
                    map.addLayer(markerClusterGroup);
                    map.fitBounds(markerClusterGroup.getBounds().pad(0.1));
                }
            }, 0);
        }
    } else {
        // Regular display for smaller datasets
        coordinates.forEach(coord => {
            const color = getMarkerColor(coord, data.top_5_stores);
            const marker = L.circleMarker([coord.latitude, coord.longitude], {
                radius: coord.is_top_5 ? 6 : 4,
                color: color,
                fillColor: color,
                fillOpacity: 0.7
            }).addTo(map);
            
            marker.bindPopup(`
                <b>${coord.store_name}</b><br>
                Store_ID: ${coord.store_id}<br>
                Visitor: ${coord.full_name}<br>
                Date: ${coord.tanggal}
                ${coord.is_top_5 ? '<br><strong style="color: ' + color + '">Top 5 Most Visited!</strong>' : ''}
            `);
            
            markers.push(marker);
        });

        if (markers.length > 0) {
            const group = new L.featureGroup(markers);
            map.fitBounds(group.getBounds().pad(0.1));
        }
    }
}

function loadMapData() {
    fetch('/api/data')
        .then(response => response.json())
        .then(data => {
            if (!data.success) {
                throw new Error(data.error || 'Failed to load data');
            }
            
            displayPoints(data, showingTop5);
            updateInfoPanel(data);
        })
        .catch(error => {
            console.error('Error:', error);
            alert(error.message);
        });
}

function updateInfoPanel(data) {
    const infoPanel = document.getElementById('info-panel');
    if (!infoPanel) return;
    
    let top5Html = '';
    if (data.top_5_stores && data.top_5_stores.length > 0) {
        top5Html = `
            <div class="top-5-section" style="margin-top: 15px;">
                <h4>Top 5 Most Visited Stores</h4>
                ${data.top_5_stores.map((store, index) => `
                    <div style="margin: 5px 0; padding: 5px; border-left: 3px solid ${store.color};">
                        #${index + 1} ${store.store_name}<br>
                        <small>${store.visit_count} visits</small>
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    const statsHtml = `
        <div class="stats-section">
            <h3>📊 Analysis Statistics</h3>
            <div class="date-range" style="background: #f0f0f0; padding: 10px; border-radius: 4px; margin-bottom: 10px;">
                <p style="margin: 0;"><strong>Period: (YYYY/MM/DD) </strong></p>
                <p style="margin: 5px 0; font-size: 1.1em;">
                    ${data.stats.date_range.start} to ${data.stats.date_range.end}
                </p>
            </div>
            <button id="toggle-top5" class="btn btn-primary" style="margin-bottom: 10px;">
                ${showingTop5 ? 'Show All Points' : 'Show Top 5 Only'}
            </button>
            <p><strong>Total Points:</strong> ${data.stats.total_points}</p>
            <p><strong>Total Stores:</strong> ${data.stats.total_stores}</p>
            ${top5Html}
        </div>
    `;
    
    infoPanel.innerHTML = statsHtml;
    
    // Add toggle button handler
    document.getElementById('toggle-top5').addEventListener('click', function() {
        showingTop5 = !showingTop5;
        this.textContent = showingTop5 ? 'Show All Points' : 'Show Top 5 Only';
        loadMapData();
    });
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initMap();
    
    // Handle file upload
    const uploadForm = document.getElementById('upload-form');
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(uploadForm);
            
            fetch('/api/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    loadMapData();
                } else {
                    throw new Error(data.error || 'Upload failed');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert(error.message);
            });
        });
    }
    
    // Handle clear data
    const clearButton = document.getElementById('clear-data');
    if (clearButton) {
        clearButton.addEventListener('click', function() {
            if (confirm('Clear all data?')) {
                fetch('/api/clear', {
                    method: 'POST'
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        clearMap();
                        document.getElementById('info-panel').innerHTML = '<p>No data loaded</p>';
                    }
                })
                .catch(error => console.error('Error:', error));
            }
        });
    }
});