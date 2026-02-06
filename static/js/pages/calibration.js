/**
 * calibration.js
 * Logic for the calibration page (Pattern generation, export)
 */

let currentPattern = null;
let currentPatternData = null;
let currentPatternId = null;

function selectPattern(type) {
    currentPattern = type;

    // Hide all configs
    document.querySelectorAll('.pattern-config').forEach(el => el.style.display = 'none');

    // Show selected config
    let configId = type.replace('_', '') + 'Config';
    let configEl = document.getElementById(configId);
    if (configEl) {
        configEl.style.display = 'block';
    }

    // Update title
    let titles = {
        'charuco': 'ChArUco Board Configuration',
        'aruco_board': 'ARUCO Board Configuration',
        'apriltag': 'AprilTag Configuration',
        'apriltag_grid': 'AprilTag Grid Configuration'
    };
    document.getElementById('configTitle').textContent = titles[type] || 'Configuration';

    // Enable generate button
    document.getElementById('generateBtn').disabled = false;

    // Highlight selected card
    document.querySelectorAll('.pattern-card').forEach(el => el.classList.remove('border-primary'));
    if (event && event.currentTarget) {
        event.currentTarget.classList.add('border-primary');
    }
}

// Make sure selectPattern is globally available if called from HTML onclick
window.selectPattern = selectPattern;

async function generatePattern() {
    if (!currentPattern) return;

    let data = {};
    let endpoint = '';

    switch (currentPattern) {
        case 'charuco':
            endpoint = '/api/calibration/charuco';
            data = {
                squares_x: parseInt(document.getElementById('charuco_squares_x').value),
                squares_y: parseInt(document.getElementById('charuco_squares_y').value),
                square_size_mm: parseFloat(document.getElementById('charuco_square_size').value),
                marker_size_mm: parseFloat(document.getElementById('charuco_marker_size').value),
                dictionary: document.getElementById('charuco_dictionary').value,
                save_to_db: true
            };
            break;

        case 'aruco_board':
            endpoint = '/api/calibration/aruco_board';
            data = {
                markers_x: parseInt(document.getElementById('board_markers_x').value),
                markers_y: parseInt(document.getElementById('board_markers_y').value),
                marker_size_mm: parseFloat(document.getElementById('board_marker_size').value),
                separation_mm: parseFloat(document.getElementById('board_separation').value),
                first_marker_id: parseInt(document.getElementById('board_first_id').value),
                dictionary: document.getElementById('board_dictionary').value,
                save_to_db: true
            };
            break;

        case 'apriltag':
            endpoint = '/api/calibration/apriltag';
            data = {
                tag_family: document.getElementById('apriltag_family').value,
                tag_id: parseInt(document.getElementById('apriltag_id').value),
                tag_size_mm: parseFloat(document.getElementById('apriltag_size').value)
            };
            break;

        case 'apriltag_grid':
            endpoint = '/api/calibration/apriltag_grid';
            data = {
                grid_x: parseInt(document.getElementById('aprilgrid_x').value),
                grid_y: parseInt(document.getElementById('aprilgrid_y').value),
                tag_size_mm: parseFloat(document.getElementById('aprilgrid_size').value),
                spacing_mm: parseFloat(document.getElementById('aprilgrid_spacing').value),
                tag_family: document.getElementById('aprilgrid_family').value,
                save_to_db: true
            };
            break;
    }

    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (result.success) {
            // Show preview
            document.getElementById('emptyPreview').style.display = 'none';
            document.getElementById('previewImage').src = 'data:image/png;base64,' + result.image_base64;
            document.getElementById('previewImage').style.display = 'block';

            // Store data
            currentPatternData = result;
            currentPatternId = result.pattern_id;

            // Show info
            let info = result.calibration_data || result.metadata;
            if (info) {
                let infoHtml = `
                    <p><strong>Dimensions:</strong> ${result.dimensions_mm[0].toFixed(1)} x ${result.dimensions_mm[1].toFixed(1)} mm</p>
                    <p><strong>Pattern Type:</strong> ${info.pattern_type || currentPattern}</p>
                `;
                if (info.total_markers) {
                    infoHtml += `<p><strong>Total Markers:</strong> ${info.total_markers}</p>`;
                }
                if (info.dictionary) {
                    infoHtml += `<p><strong>Dictionary:</strong> ${info.dictionary}</p>`;
                }
                document.getElementById('infoContent').innerHTML = infoHtml;
                document.getElementById('patternInfo').style.display = 'block';
            }

            // Enable download buttons
            document.getElementById('downloadBtn').disabled = false;
            if (currentPatternId) {
                document.getElementById('yamlBtn').disabled = false;
                document.getElementById('jsonBtn').disabled = false;
                document.getElementById('rosBtn').disabled = false;
            }
        } else {
            alert('Error: ' + result.error);
        }
    } catch (error) {
        alert('Failed to generate pattern: ' + error);
    }
}
window.generatePattern = generatePattern;

function downloadPattern() {
    if (!currentPatternData || !currentPatternData.image_base64) return;

    // Convert base64 to blob
    const base64 = currentPatternData.image_base64;
    const binary = atob(base64);
    const array = [];
    for (let i = 0; i < binary.length; i++) {
        array.push(binary.charCodeAt(i));
    }
    const blob = new Blob([new Uint8Array(array)], { type: 'image/png' });

    // Create download link
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${currentPattern}_pattern.png`;
    a.click();
    URL.revokeObjectURL(url);
}
window.downloadPattern = downloadPattern;

async function exportData(format) {
    if (!currentPatternId) return;

    window.location.href = `/api/calibration/export/${currentPatternId}?format=${format}`;
}
window.exportData = exportData;
