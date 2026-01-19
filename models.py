from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prompt = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending') # pending, processing, completed, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    scad_code = db.Column(db.Text)
    error_message = db.Column(db.Text)
    
    # Paths relative to static folder
    scad_filename = db.Column(db.String(100))
    stl_filename = db.Column(db.String(100))
    png_filename = db.Column(db.String(100))

    def __repr__(self):
        return f'<Job {self.id}: {self.status}>'
