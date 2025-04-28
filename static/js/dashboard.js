/**
 * Fintelligence - Dashboard JavaScript
 * Handles dashboard-specific functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // File upload functionality
    setupFileUpload();
    
    // Initialize any dashboard charts
    initializeDashboardCharts();
    
    // Handle report generation actions
    setupReportGeneration();
});

/**
 * Setup file upload drag and drop functionality
 */
function setupFileUpload() {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const filePreview = document.getElementById('filePreview');
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');
    const removeFile = document.getElementById('removeFile');
    const uploadButton = document.getElementById('uploadButton');
    const uploadForm = document.getElementById('uploadForm');
    
    if (!dropZone || !fileInput) return;
    
    // Handle click on drop zone
    dropZone.addEventListener('click', function() {
        fileInput.click();
    });
    
    // Handle drag and drop events
    ['dragover', 'dragenter'].forEach(eventName => {
        dropZone.addEventListener(eventName, function(e) {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.add('border-primary');
        }, false);
    });
    
    ['dragleave', 'dragend'].forEach(eventName => {
        dropZone.addEventListener(eventName, function(e) {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.remove('border-primary');
        }, false);
    });
    
    dropZone.addEventListener('drop', function(e) {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.remove('border-primary');
        
        if (e.dataTransfer.files.length) {
            fileInput.files = e.dataTransfer.files;
            updateFilePreview(e.dataTransfer.files[0]);
        }
    }, false);
    
    // Handle file selection through input
    fileInput.addEventListener('change', function() {
        if (fileInput.files.length) {
            updateFilePreview(fileInput.files[0]);
        }
    });
    
    // Remove selected file
    if (removeFile) {
        removeFile.addEventListener('click', function(e) {
            e.preventDefault();
            fileInput.value = '';
            filePreview.classList.add('d-none');
            uploadButton.disabled = true;
        });
    }
    
    // Handle form submission
    if (uploadButton && uploadForm) {
        uploadButton.addEventListener('click', function() {
            // Show loading state
            uploadButton.disabled = true;
            uploadButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Uploading...';
            
            // Submit the form
            uploadForm.submit();
        });
    }
    
    /**
     * Update file preview after selection
     * @param {File} file - The selected file
     */
    function updateFilePreview(file) {
        if (!fileName || !fileSize || !filePreview || !uploadButton) return;
        
        // Validate file type
        const validTypes = ['.csv', '.xlsx', '.pdf'];
        const fileExt = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
        
        if (!validTypes.includes(fileExt)) {
            // Show error for invalid file type
            alert('Invalid file type. Please select a CSV, XLSX, or PDF file.');
            fileInput.value = '';
            return;
        }
        
        // Update file preview UI
        fileName.textContent = file.name;
        fileSize.textContent = formatFileSize(file.size);
        filePreview.classList.remove('d-none');
        uploadButton.disabled = false;
        
        // Set file icon based on type
        const fileIcon = filePreview.querySelector('.fas');
        if (fileIcon) {
            if (fileExt === '.csv') {
                fileIcon.className = 'fas fa-file-csv text-success me-3 fa-2x';
            } else if (fileExt === '.xlsx') {
                fileIcon.className = 'fas fa-file-excel text-success me-3 fa-2x';
            } else if (fileExt === '.pdf') {
                fileIcon.className = 'fas fa-file-pdf text-danger me-3 fa-2x';
            } else {
                fileIcon.className = 'fas fa-file-alt text-primary me-3 fa-2x';
            }
        }
    }
    
    /**
     * Format file size to human-readable format
     * @param {number} bytes - File size in bytes
     * @return {string} Formatted file size
     */
    function formatFileSize(bytes) {
        if (bytes < 1024) {
            return bytes + ' bytes';
        } else if (bytes < 1024 * 1024) {
            return (bytes / 1024).toFixed(2) + ' KB';
        } else {
            return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
        }
    }
}

/**
 * Initialize dashboard overview charts if they exist
 */
function initializeDashboardCharts() {
    // Check if overview chart containers exist
    const recentUploadsChart = document.getElementById('recentUploadsChart');
    const reportTypesChart = document.getElementById('reportTypesChart');
    
    // Initialize recent uploads chart if it exists
    if (recentUploadsChart) {
        createRecentUploadsChart();
    }
    
    // Initialize report types distribution chart if it exists
    if (reportTypesChart) {
        createReportTypesChart();
    }
}

/**
 * Create recent uploads activity chart
 */
function createRecentUploadsChart() {
    // Get the chart context
    const ctx = document.getElementById('recentUploadsChart');
    if (!ctx) return;
    
    // Sample data - in production this would come from the backend
    const activityData = {
        labels: ['7 days ago', '6 days ago', '5 days ago', '4 days ago', '3 days ago', '2 days ago', 'Yesterday'],
        datasets: [{
            label: 'Files Uploaded',
            data: [1, 2, 1, 3, 2, 4, 2],
            backgroundColor: chartColors.primaryLight,
            borderColor: chartColors.primary,
            borderWidth: 1
        }]
    };
    
    // Create chart
    new Chart(ctx, {
        type: 'bar',
        data: activityData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

/**
 * Create report types distribution chart
 */
function createReportTypesChart() {
    // Get the chart context
    const ctx = document.getElementById('reportTypesChart');
    if (!ctx) return;
    
    // Sample data - in production this would come from the backend
    const typeData = {
        labels: ['Balance Sheets', 'Income Statements', 'Cash Flow'],
        datasets: [{
            data: [5, 7, 4],
            backgroundColor: [
                chartColors.primary,
                chartColors.success,
                chartColors.info
            ],
            hoverBackgroundColor: [
                chartColors.primary,
                chartColors.success, 
                chartColors.info
            ],
            hoverBorderColor: "rgba(234, 236, 244, 1)",
        }]
    };
    
    // Create chart
    new Chart(ctx, {
        type: 'doughnut',
        data: typeData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '70%',
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

/**
 * Setup report generation button handlers
 */
function setupReportGeneration() {
    // Get all report generation buttons
    const reportButtons = document.querySelectorAll('[data-action="generate-report"]');
    
    reportButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const fileId = this.dataset.fileId;
            const reportType = this.dataset.reportType;
            
            if (!fileId || !reportType) return;
            
            // Show loading state
            const originalText = this.innerHTML;
            this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Generating...';
            this.disabled = true;
            
            // Redirect to the report generation URL
            window.location.href = `/generate_report/${fileId}/${reportType}`;
        });
    });
}
