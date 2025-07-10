let map;
let markers = [];
let markerClusterGroup = null;
let showingTop5 = false;

function initMap() {
    map = L.map('map').setView([-6.2088, 106.8456], 10);
    
    // Replace your existing tileLayer with this
    L.tileLayer('https://{s}.tile.jawg.io/jawg-streets/{z}/{x}/{y}{r}.png?access-token=IGbEI5YqiZJzxgxVplq1cIkR7K41bYxy1CoDm2xmtv83shMfGR0KGnWrFb7k77E4', {
        attribution: '<a href="http://jawg.io" title="Tiles Courtesy of Jawg Maps" target="_blank">&copy; <b>Jawg</b>Maps</a>',
        minZoom: 0,
        maxZoom: 22,
        subdomains: 'abcd',
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
        if (storeInfo) {
            // Define high contrast colors for top 5 stores
            const contrastColors = [
                '#FF0000', // Bright Red
                '#00FF00', // Bright Green  
                '#0000FF', // Bright Blue
                '#FF00FF', // Bright Magenta
                '#FF8000'  // Bright Orange
            ];
            const storeIndex = top5Stores.indexOf(storeInfo);
            return contrastColors[storeIndex] || '#FF0000';
        }
        return '#FF0000'; // Fallback red for top 5
    }
    return '#3388ff'; // Default blue for regular points
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
                        color: coord.is_top_5 ? '#000000' : color, // Black outline for top 5
                        weight: coord.is_top_5 ? 2 : 1, // Thicker outline for top 5
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
                color: coord.is_top_5 ? '#000000' : color, // Black outline for top 5
                weight: coord.is_top_5 ? 0.5 : 0.2, // Thicker outline for top 5
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
    
    const headerHtml = `
        <div class="analysis-header">
            <h3 style="margin: 0; color: #2c3e50;">📊 Analysis Statistics</h3>
        </div>
    `;
    
    const contentHtml = `
        <div class="analysis-content">
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
    
    infoPanel.innerHTML = headerHtml + contentHtml;
    
    // Add toggle button handler
    document.getElementById('toggle-top5').addEventListener('click', function() {
        showingTop5 = !showingTop5;
        this.textContent = showingTop5 ? 'Show All Points' : 'Show Top 5 Only';
        loadMapData();
    });
}

// File input handling function
function setupFileHandling() {
    const fileInput = document.getElementById('csv-file');
    const fileLabel = document.querySelector('.file-input-label');
    const fileNameDisplay = document.getElementById('file-name-display');
    const uploadBtn = document.getElementById('upload-btn');
    const removeBtn = document.getElementById('remove-file');
    
    if (!fileInput || !fileLabel || !fileNameDisplay || !uploadBtn || !removeBtn) return;
    
    fileInput.addEventListener('change', function() {
        const file = this.files[0];
        if (file) {
            // Show file name
            fileNameDisplay.textContent = file.name;
            fileNameDisplay.style.display = 'block';
            
            // Show upload and remove buttons
            uploadBtn.style.display = 'inline-block';
            removeBtn.style.display = 'inline-block';
            
            // Update label text
            fileLabel.textContent = 'Change File';
        } else {
            resetFileDisplay();
        }
    });
    
    removeBtn.addEventListener('click', function() {
        fileInput.value = '';
        resetFileDisplay();
    });
    
    function resetFileDisplay() {
        fileNameDisplay.style.display = 'none';
        uploadBtn.style.display = 'none';
        removeBtn.style.display = 'none';
        fileLabel.textContent = 'Choose CSV File';
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initMap();
    setupFileHandling();
    
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
                        showEmptyAnalysisPanel();
                    }
                })
                .catch(error => console.error('Error:', error));
            }
        });
    }
    
    // Show empty analysis panel on initial load
    showEmptyAnalysisPanel();
});

// Add this new function to show empty analysis panel
function showEmptyAnalysisPanel() {
    const infoPanel = document.getElementById('info-panel');
    if (!infoPanel) return;
    
    const headerHtml = `
        <div class="analysis-header">
            <h3 style="margin: 0; color: #2c3e50;">📊 Analysis Statistics</h3>
        </div>
    `;
    
    const contentHtml = `
        <div class="analysis-content">
            <div class="date-range" style="background: #f0f0f0; padding: 10px; border-radius: 4px; margin-bottom: 10px;">
                <p style="margin: 0; color: #666;">Upload a CSV file to view date range</p>
            </div>
            <div style="text-align: center; padding: 20px; color: #666;">
                <p>Information will be displayed here after uploading data</p>
                <p><small>You will see:</small></p>
                <ul style="text-align: left; color: #666;">
                    <li>Total visited points</li>
                    <li>Total unique stores</li>
                    <li>Top 5 most visited stores</li>
                </ul>
            </div>
        </div>
    `;
    
    infoPanel.innerHTML = headerHtml + contentHtml;
}