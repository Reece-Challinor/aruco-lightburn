import { parseCalibration, exportOpenCV, exportROSJSON, exportROSYAML, exportKalibr } from '/static/js/lib/format-adapters.js';

document.addEventListener('DOMContentLoaded', () => {
    const els = {
        uploadZone: document.getElementById('upload-zone'),
        fileInput: document.getElementById('file-input'),
        pasteArea: document.getElementById('paste-area'),
        emptyState: document.getElementById('empty-state'),
        resultsState: document.getElementById('results-state'),
        resResolution: document.getElementById('res-resolution'),
        resCameraMatrix: document.getElementById('res-camera-matrix'),
        resDistModel: document.getElementById('res-dist-model'),
        resDistCoeffs: document.getElementById('res-dist-coeffs'),
        exportFormat: document.getElementById('export-format'),
        exportPreview: document.getElementById('export-preview'),
        btnDownload: document.getElementById('btn-download'),
        btnCopy: document.getElementById('btn-copy')
    };

    let currentCanonical = null;

    function handleInput(content) {
        if (!content || !content.trim()) {
            els.emptyState.style.display = 'block';
            els.resultsState.style.display = 'none';
            currentCanonical = null;
            return;
        }

        try {
            currentCanonical = parseCalibration(content);
            updatePreview();
            els.emptyState.style.display = 'none';
            els.resultsState.style.display = 'block';
            if (els.pasteArea.value !== content) {
                els.pasteArea.value = content;
            }
        } catch (e) {
            window.notificationManager?.showError(e.message);
            els.emptyState.style.display = 'block';
            els.resultsState.style.display = 'none';
            currentCanonical = null;
        }
    }

    function updatePreview() {
        if (!currentCanonical) return;

        // Update C-20 comparison table
        els.resResolution.textContent = `${currentCanonical.resolution.width} × ${currentCanonical.resolution.height}`;
        const cm = currentCanonical.camera_matrix;
        if (cm && cm.length >= 9) {
            els.resCameraMatrix.textContent = `fx: ${cm[0].toFixed(2)}, fy: ${cm[4].toFixed(2)}, cx: ${cm[2].toFixed(2)}, cy: ${cm[5].toFixed(2)}`;
        }
        els.resDistModel.textContent = currentCanonical.distortion_model;
        els.resDistCoeffs.textContent = `[${currentCanonical.distortion_coeffs.map(n => n.toFixed(4)).join(', ')}]`;

        // Update Export Textarea
        const format = els.exportFormat.value;
        let exported = '';
        if (format === 'opencv') exported = exportOpenCV(currentCanonical);
        else if (format === 'ros_json') exported = exportROSJSON(currentCanonical);
        else if (format === 'ros_yaml') exported = exportROSYAML(currentCanonical);
        else if (format === 'kalibr') exported = exportKalibr(currentCanonical);

        els.exportPreview.value = exported;
    }

    // Drag and Drop
    els.uploadZone.addEventListener('dragover', e => {
        e.preventDefault();
        els.uploadZone.classList.replace('border-secondary', 'border-primary');
    });
    els.uploadZone.addEventListener('dragleave', e => {
        e.preventDefault();
        els.uploadZone.classList.replace('border-primary', 'border-secondary');
    });
    els.uploadZone.addEventListener('drop', e => {
        e.preventDefault();
        els.uploadZone.classList.replace('border-primary', 'border-secondary');
        if (e.dataTransfer.files.length) {
            const file = e.dataTransfer.files[0];
            const reader = new FileReader();
            reader.onload = e => handleInput(e.target.result);
            reader.readAsText(file);
        }
    });

    // File Input
    els.uploadZone.addEventListener('click', () => els.fileInput.click());
    els.fileInput.addEventListener('change', e => {
        if (e.target.files.length) {
            const reader = new FileReader();
            reader.onload = e => handleInput(e.target.result);
            reader.readAsText(e.target.files[0]);
        }
    });

    // Paste Area
    els.pasteArea.addEventListener('input', e => {
        handleInput(e.target.value);
    });

    // Format Change
    els.exportFormat.addEventListener('change', updatePreview);

    // Download
    els.btnDownload.addEventListener('click', () => {
        if (!currentCanonical) return;
        const format = els.exportFormat.value;
        let ext = '.yaml';
        if (format === 'ros_json') ext = '.json';

        const blob = new Blob([els.exportPreview.value], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `calibration_${format}${ext}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    });

    // Copy
    els.btnCopy.addEventListener('click', () => {
        if (!currentCanonical) return;
        navigator.clipboard.writeText(els.exportPreview.value).then(() => {
            window.notificationManager?.showSuccess('Copied to clipboard');
        });
    });
});
