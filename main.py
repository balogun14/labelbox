from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import crud, schemas, models
from minio_client import upload_file_to_minio

# Initialize database tables
models.Base.metadata.create_all(bind=engine)

# Custom metadata for Swagger
app = FastAPI(
    title="Challenge Collaboration API",
    description="An API to create and manage challenges, upload files to MinIO, and retrieve them.",
    version="1.0.0",
    contact={
        "name": "Awwal",
        "email": "awwalbalogun87@gmail.com",  
        "url": "https://github.com/balogun14", 
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post(
    "/challenges/",
    response_model=schemas.Challenge,
    tags=["Challenges"],
    summary="Create a new challenge",
    description="Create a new challenge by providing a title, description, and an optional file upload. Maximum file upload is 10Mb",
)
async def create_challenge(
    title: str,
    description: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Create a new challenge with a file upload.
    """
    try:
        # Upload file to MinIO
        file_url = upload_file_to_minio(file)
        challenge = schemas.ChallengeCreate(
            title=title,
            description=description,
            file_url=file_url
        )
        return crud.create_challenge(db=db, challenge=challenge)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/challenges/",
    response_model=list[schemas.Challenge],
    tags=["Challenges"],
    summary="Retrieve all challenges",
    description="Get a list of all challenges with pagination options.",
)
def get_challenges(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Retrieve all challenges with pagination.
    """
    return crud.get_challenges(db=db, skip=skip, limit=limit)
