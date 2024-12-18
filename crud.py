from sqlalchemy.orm import Session
import models, schemas

def create_challenge(db: Session, challenge: schemas.ChallengeCreate):
    db_challenge = models.Challenge(
        title=challenge.title,
        description=challenge.description,
        file_url=challenge.file_url,
    )
    db.add(db_challenge)
    db.commit()
    db.refresh(db_challenge)
    return db_challenge


def get_challenges(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Challenge).offset(skip).limit(limit).all()
