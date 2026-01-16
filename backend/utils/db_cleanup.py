from app import app
from models import db, URLCheck

def delete_ids(ids):
    with app.app_context():
        for i in ids:
            record = db.session.get(URLCheck, i)
            if record:
                db.session.delete(record)
        db.session.commit()
        print(f"Deleted IDs: {ids}")

if __name__ == "__main__":
    delete_ids([10, 11])
