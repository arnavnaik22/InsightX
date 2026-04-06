$(document).ready(function() {
    
    // Toast Notification System
    function showToast(message, type = 'primary') {
        const toastHtml = `
        <div class="toast align-items-center text-bg-${type} border-0 show" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>`;
        const container = $('#toastContainer');
        const el = $(toastHtml).appendTo(container);
        setTimeout(() => el.remove(), 5000);
    }

    // Dark Mode Toggle logic
    const toggleBtn = $('#darkModeToggle');
    const body = $('#appBody');
    let isDark = localStorage.getItem('darkMode') === 'true';

    function applyDark(state) {
        if (state) {
            body.addClass('bg-dark-mode');
            $('html').attr('data-bs-theme', 'dark');
            toggleBtn.html('<i class="bi bi-sun"></i>');
        } else {
            body.removeClass('bg-dark-mode');
            $('html').removeAttr('data-bs-theme');
            toggleBtn.html('<i class="bi bi-moon"></i>');
        }
    }
    applyDark(isDark);
    toggleBtn.on('click', function() {
        isDark = !isDark;
        localStorage.setItem('darkMode', isDark);
        applyDark(isDark);
    });

    // JD Template Logic
    $('#jdTemplateSelect').on('change', function() {
        const val = $(this).val();
        if(val) {
            $('#jdTextarea').val(val);
        } else {
            $('#jdTextarea').val('');
        }
    });

    // File upload zone
    const dropZone = $('#dropZone');
    const fileInput = $('#resumeFile');
    const fileLabel = $('#fileLabel');

    // Show filename when selected via dialog
    fileInput.on('change', function() {
        if (this.files.length) {
            fileLabel.text(this.files[0].name);
        }
    });

    // Drag and drop support
    if (dropZone.length) {
        dropZone.on('dragover', function(e) {
            e.preventDefault();
            dropZone.addClass('bg-primary bg-opacity-10 border-primary');
        });
        dropZone.on('dragleave', function(e) {
            e.preventDefault();
            dropZone.removeClass('bg-primary bg-opacity-10 border-primary');
        });
        dropZone.on('drop', function(e) {
            e.preventDefault();
            dropZone.removeClass('bg-primary bg-opacity-10 border-primary');
            const files = e.originalEvent.dataTransfer.files;
            if (files.length) {
                // Assign dropped files to the real input using DataTransfer
                const dt = new DataTransfer();
                dt.items.add(files[0]);
                fileInput[0].files = dt.files;
                fileLabel.text(files[0].name);
            }
        });
    }

    // Form Submission
    $('#analyzeForm').on('submit', function(e) {
        e.preventDefault();

        const jdText = $('#jdTextarea').val().trim();
        const file = fileInput[0].files[0];

        if (!jdText) {
            showToast('Please paste a Job Description.', 'danger');
            return;
        }
        if (!file) {
            showToast('Please select a PDF resume.', 'danger');
            return;
        }
        if (file.size > 5 * 1024 * 1024) {
            showToast('File too large. Max 5MB.', 'danger');
            return;
        }

        const fd = new FormData();
        fd.append('jd_text', jdText);
        fd.append('resume_file', file);
        fd.append('csrfmiddlewaretoken', $('[name=csrfmiddlewaretoken]').val());

        $('#analyzeForm').addClass('d-none');
        $('#loadingState').removeClass('d-none');

        $.ajax({
            url: '/analyze/',
            type: 'POST',
            data: fd,
            processData: false,
            contentType: false,
            success: function(res) {
                if (res.status === 'pending') {
                    showToast('Analysis queued in background.', 'info');
                    pollStatus(res.task_id);
                } else if (res.status === 'success') {
                    showToast('Analysis successful!', 'success');
                    window.location.href = `/analysis/${res.analysis_id}/`;
                } else {
                    showError(res.message || 'Unknown error.');
                }
            },
            error: function(xhr) {
                let msg = 'An error occurred.';
                try { msg = xhr.responseJSON.message || xhr.responseJSON.error; } catch(e) {}
                showError(msg);
            }
        });
    });

    function pollStatus(taskId) {
        const interval = setInterval(function() {
            $.get(`/analyze/status/${taskId}/`, function(res) {
                if (res.status === 'COMPLETED') {
                    clearInterval(interval);
                    window.location.href = `/analysis/${res.analysis_id}/`;
                } else if (res.status === 'FAILED') {
                    clearInterval(interval);
                    showError('Analysis failed during processing.');
                }
            }).fail(function() {
                clearInterval(interval);
                showError('Error checking analysis status.');
            });
        }, 2000);
    }

    function showError(msg) {
        $('#analyzeForm').removeClass('d-none');
        $('#loadingState').addClass('d-none');
        showToast(msg, 'danger');
    }

});
