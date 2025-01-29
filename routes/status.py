
from flask import jsonify
from models import ImportJob
from . import api

@api.route('/status/<job_id>', methods=['GET'])
def get_status(job_id):
    job = ImportJob.query.get_or_404(job_id)
    return jsonify({
        "status": job.status,
        "processed_rows": job.processed_rows,
        "total_rows": job.total_rows,
        "current_batch": job.current_batch,
        "total_batches": (job.total_rows + job.batch_size - 1) // job.batch_size if job.batch_size else 0,
        "error_message": job.error_message
    })
